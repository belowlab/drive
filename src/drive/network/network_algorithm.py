import json
from pathlib import Path
import polars as pl
from datetime import datetime

from log import CustomLogger

import drive.network.factory as factory
from drive.network.cluster import ClusterHandler, cluster
from drive.models import create_indices, IbdFileIndices
from drive.network.models import RuntimeState
from drive.helper_funcs import split_target_string
from drive.parser import (
    PhenotypeFileParser,
    load_phenotype_descriptions,
    PhecodesMapper,
)
from drive.filters import DuckdbTemplate, DuckDBFilter, filter_ibd_file

logger = CustomLogger.get_logger(__name__)


def find_json_file() -> Path:
    """Method to find the default config file if the user does not provide one

    Returns
    -------
    Path
        returns the path to the json file

    Raises
    ------
    FileNotFoundError
        Raises a FileNotFoundError if the program can not locate a json file and the
        user does not provide the path to a file
    """

    src_dir = Path(__file__).parent.parent

    config_path = src_dir / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Expected the user to either pass a configuration file path or for the config.json file to be present in the program root directory at {config_path}."  # noqa: E501
        )

    return config_path


def generate_vertex_info_df(
    data: pl.DataFrame, indices: IbdFileIndices
) -> pl.DataFrame:
    """create a dataframe that has just the the idnum, the hapid, and the grid id

    Parameters
    ----------
    pl.DataFrame
        dataframe that has information about the pairwise IBD segments. By this point
        in the code it should have the following columns 'hapid1', 'hapid2', 'idnum1',
        and 'idnum2'

    indice: IbdFileIndices
        namedtuple where each attribute is the right name of columns in the dataframe

    Returns
    -------
    pl.DataFrame
        returns the dataframe representing all the vertices in the graph. Each row is
        a vertex with the haplotype integer id (idnum), haplotype string id (hapid)
        and the original individual id (hapid without the phase indicator)
    """
    vertex_df = pl.concat(
        [
            data.select(pl.col("idnum1", "hapid1", indices.id1_indx)).rename(
                {"idnum1": "idnum", "hapid1": "hapID", indices.id1_indx: "IID"}
            ),
            data.select(pl.col("idnum2", "hapid2", indices.id2_indx)).rename(
                {"idnum2": "idnum", "hapid2": "hapID", indices.id2_indx: "IID"}
            ),
        ]
    )

    return vertex_df.unique().sort("idnum")


def generate_edge_info_df(
    data: pl.DataFrame, indices: IbdFileIndices
) -> tuple[pl.DataFrame, dict[int, str]]:
    """map the hapids columns to a unique integer id that is needed for igraph

    Parameters
    ----------
    pl.DataFrame
        dataframe that has information about the pairwise IBD segments. By this point in the code it should have two columns 'hapid1' and 'hapid2'

    Returns
    -------
    tuple[pl.DataFrame, dict[int, str]]
        returns a dataframe that represents all of the edges in the
        graph. It has columns for id1 and id2 and then the length of the
        edge between them. also returns a dictionary of the haplotype mappings where the keys are the integer mapped haplotype id and the values are the string haplotype id before mapping
    """
    unique_mapping = (
        pl.concat(
            [
                data.select(pl.col("hapid1").alias("IDs")),
                data.select(pl.col("hapid2").alias("IDs")),
            ]
        )
        .unique()
        .with_row_index("haplotype_mapping")
    )

    edge_list_df = (
        data.join(unique_mapping, left_on="hapid1", right_on="IDs", how="left")
        .rename({"haplotype_mapping": "id1_new"})
        .join(unique_mapping, left_on="hapid2", right_on="IDs", how="left")
        .rename({"haplotype_mapping": "id2_new"})
        .select(
            [
                "id1_new",
                "id2_new",
                "hapid1",
                "hapid2",
                indices.cM_indx,
                indices.id1_indx,
                indices.id2_indx,
            ]
        )
        .rename(
            {"id1_new": "idnum1", "id2_new": "idnum2", indices.cM_indx: "cm"}
        )  # These are the columns we need to use in igraph
    )

    # Lets also generate a dictionary map of the haplotpes to there ids for later on in the code
    haplotype_mapping_dict = dict(
        zip(
            unique_mapping.get_column("haplotype_mapping"),
            unique_mapping.get_column("IDs"),
        )
    )
    return edge_list_df, haplotype_mapping_dict


def run_network_identification(args) -> None:
    """main entrypoint to run the clustering algorithm for DRIVE"""
    # record analysis start time
    start_time = datetime.now()
    # We need to make sure that there is a configuration file
    json_config = args.json_config if args.json_config else find_json_file()

    assert (
        json_config is not None
    ), "No configuration file was detected for DRIVE. This means that the configuration file packaged with DRIVE has been deleted. Please re-download this file from the Github"

    # we need to load in the phenotype descriptions file to get
    # descriptions of each phenotype
    logger.debug("Loading all phecode mappings for versions 1.2 and X")

    phecodeDescriptions = PhecodesMapper()
    load_phenotype_descriptions(phecodeDescriptions)
    logger.debug(
        f"Loading in mappings for {len(phecodeDescriptions.phecode_names)} phecodes from both versions 1.2 and X"
    )

    # if the user has provided a phenotype file then we will determine case/control/
    # exclusion counts. Otherwise we return an empty dictionary
    if args.cases:
        with PhenotypeFileParser(args.cases, args.phenotype_name) as phenotype_file:
            phenotype_counts, cohort_ids = phenotype_file.parse_cases_and_controls()

            logger.info(
                f"identified {len(phenotype_counts.keys())} phenotypes within the file {args.cases}"  # noqa: E501
            )
            filter_samples = True
    else:
        logger.info(
            "No phenotype information provided. Only the clustering step of the analysis will be performed"  # noqa: E501
        )

        phenotype_counts = {}
        cohort_ids = []
        filter_samples = False

    indices = create_indices(args.format.lower())

    logger.debug(f"created indices object: {indices}")

    ##target gene region or variant position
    target_gene = split_target_string(args.target)

    logger.debug(f"Identified a target region: {target_gene}")

    # Now we need to connect the new filtering process
    # generate filter with overlaps or contains logic
    segment_filter = DuckDBFilter(indices, target_gene, args.segment_overlap)

    sql_query = DuckdbTemplate(
        ibd_segment_file=args.input,
        filterObj=segment_filter,
        indices=indices,
        min_cm=args.min_cm,
    ).get_network_filter(add_sample_filter=filter_samples)

    # We need to convert the cohort id list to a dataframe
    cohort_id_df = pl.DataFrame({"IDs": cohort_ids})

    filtered_ibd_df = filter_ibd_file(
        sql_query=sql_query, keep_df=cohort_id_df, indices=indices
    )

    edge_info_df, haplotype_mappings = generate_edge_info_df(
        data=filtered_ibd_df, indices=indices
    )

    logger.verbose(
        f"Gathered information for {edge_info_df.shape[0]} edges within the dataset"
    )

    vertex_info_df = generate_vertex_info_df(data=edge_info_df, indices=indices)

    logger.verbose(
        f"Gathered information for {vertex_info_df.shape[0]} vertices within the dataset"
    )
    logger.info("Beginning clustering analysis")
    # creating the object that will handle clustering within the networks
    cluster_handler = ClusterHandler(
        args.min_connected_threshold,
        args.max_network_size,
        args.max_recheck,
        args.step,
        args.min_network_size,
        args.segment_distribution_threshold,
        args.hub_threshold,
        haplotype_mappings,
        args.recluster,
    )

    # igraph accepts pandas df not polars so we need to convert the polars
    # df to pandas df.
    edge_pandas_df = edge_info_df.select(pl.col(["idnum1", "idnum2", "cm"])).to_pandas()

    vertex_pandas_df = vertex_info_df.to_pandas()

    networks = cluster(
        edge_info_df=edge_pandas_df,
        vertix_info_df=vertex_pandas_df,
        cluster_obj=cluster_handler,
    )

    # Record information about how long the clustering process took
    end_time = datetime.now()

    logger.verbose(
        f"Finished the clustering analysis. Time took: {end_time - start_time}"
    )

    # creating the data container that all the plugins can interact with
    plugin_api = RuntimeState(
        networks,
        args.output,
        phenotype_counts,
        phecodeDescriptions,
        config_options={
            "compress": args.compress_output,
            "phecode_categories_to_keep": args.phecode_categories_to_keep,
            "split_phecode_categories": args.split_phecode_categories,
        },
    )

    logger.debug(f"Data container: {plugin_api}")

    # making sure that the output directory is created
    # This section will load in the analysis plugins and run each plugin
    with open(json_config, encoding="utf-8") as json_config:
        config = json.load(json_config)

        factory.load_plugins(config["plugins"])

        analysis_plugins = [factory.factory_create(item) for item in config["modules"]]

        logger.debug(
            f"Using plugins: {', '.join([obj.name for obj in analysis_plugins])}"
        )

        # iterating over every plugin and then running the analyze and write method
        for analysis_obj in analysis_plugins:
            analysis_obj.analyze(data=plugin_api)
