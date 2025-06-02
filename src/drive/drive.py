import argparse
import json
import re
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from log import CustomLogger
from rich_argparse import RichHelpFormatter

import drive.factory as factory
from drive.cluster import ClusterHandler, cluster
from drive.filters import IbdFilter
from drive.models import Data, Genes, create_indices
from drive.utilities.callbacks import CheckInputExist
from drive.utilities.parser import PhenotypeFileParser, load_phenotype_descriptions, generate_cmd_parser


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

    src_dir = Path(__file__).parent

    config_path = src_dir / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Expected the user to either pass a configuration file path or for the config.json file to be present in the program root directory at {config_path}."  # noqa: E501
        )

    return config_path


def split_target_string(chromo_pos_str: str) -> Genes:
    """Function that will split the target string provided by the user.

    Parameters
    ----------
    chromo_pos_str : str
        String that has the region of interest in base pairs.
        This string will look like 10:1234-1234 where the
        first number is the chromosome number, then the start
        position, and then the end position of the region of
        interest.

    Returns
    -------
    Genes
        returns a namedtuple that has the chromosome number,
        the start position, and the end position

    Raises
    ------
    ValueError
        raises a value error if the string was formatted any
        other way than chromosome:start_position-end_position.
        Also raises a value error if the start position is
        larger than the end position
    """
    split_str = re.split(":|-", chromo_pos_str)

    if len(split_str) != 3:
        error_msg = f"Expected the gene position string to be formatted like chromosome:start_position-end_position. Instead it was formatted as {chromo_pos_str}"  # noqa: E501

        raise ValueError(error_msg)

    integer_split_str = [int(value) for value in split_str]

    if integer_split_str[1] > integer_split_str[2]:
        raise ValueError(
            f"expected the start position of the target string to be <= the end position. Instead the start position was {integer_split_str[1]} and the end position was {integer_split_str[2]}"  # noqa: E501
        )

    return Genes(*integer_split_str)


def main() -> None:
    parser = generate_cmd_parser()

    args = parser.parse_args()

    # getting the programs start time
    start_time = datetime.now()

    # We need to make sure that there is a configuration file
    json_config = args.json_config if args.json_config else find_json_file()

    # creating and configuring the logger and then recording user inputs
    logger = CustomLogger.create_logger()

    logger.configure(
        args.output.parent, args.log_filename, args.verbose, args.log_to_console
    )

    logger.info(f"DRIVE version: {version('drive-ibd')}")

    # record the input parameters using a method from the logger object that
    # takes the parser as an argument
    logger.record_namespace(args)

    logger.debug(f"Parent directory for log files and output: {args.output.parent}")

    logger.info(f"Analysis start time: {start_time}")
    # we need to load in the phenotype descriptions file to get
    # descriptions of each phenotype
    if args.descriptions:
        logger.verbose(f"Using the phenotype descriptions file at: {args.descriptions}")
        desc_dict = load_phenotype_descriptions(args.descriptions)
    else:
        logger.verbose("No phenotype descriptions provided")
        desc_dict = {}

    # if the user has provided a phenotype file then we will determine case/control/
    # exclusion counts. Otherwise we return an empty dictionary
    if args.cases:
        with PhenotypeFileParser(args.cases, args.phenotype_name) as phenotype_file:
            phenotype_counts, cohort_ids = phenotype_file.parse_cases_and_controls()

            logger.info(
                f"identified {len(phenotype_counts.keys())} phenotypes within the file {args.cases}"  # noqa: E501
            )
    else:
        logger.info(
            "No phenotype information provided. Only the clustering step of the analysis will be performed"  # noqa: E501
        )

        phenotype_counts = {}
        cohort_ids = {}

    indices = create_indices(args.format.lower())

    logger.debug(f"created indices object: {indices}")

    ##target gene region or variant position
    target_gene = split_target_string(args.target)

    logger.debug(f"Identified a target region: {target_gene}")

    filter_obj: IbdFilter = IbdFilter.load_file(args.input, indices, target_gene)

    # choosing the proper way to filter the ibd files
    filter_obj.set_filter(args.segment_overlap)

    filter_obj.preprocess(args.min_cm, cohort_ids)

    # We need to invert the hapid_map dictionary so that the
    # integer mappings are keys and the values are the
    # haplotype string
    hapid_inverted = {value: key for key, value in filter_obj.hapid_map.items()}

    # creating the object that will handle clustering within the networks
    cluster_handler = ClusterHandler(
        args.min_connected_threshold,
        args.max_network_size,
        args.max_recheck,
        args.step,
        args.min_network_size,
        args.segment_distribution_threshold,
        args.hub_threshold,
        hapid_inverted,
        args.recluster,
    )

    networks = cluster(filter_obj, cluster_handler, indices.cM_indx)

    # creating the data container that all the plugins can interact with
    plugin_api = Data(networks, args.output, phenotype_counts, desc_dict)

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

    end_time = datetime.now()

    logger.info(
        f"Analysis finished at {end_time}. Total runtime: {end_time - start_time}"
    )


if __name__ == "__main__":
    main()
