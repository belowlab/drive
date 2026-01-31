from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy.typing as npt
import pandas as pd
import polars as pl
import scipy.cluster.hierarchy as sch
from log import CustomLogger
from numpy import zeros
from scipy.spatial.distance import squareform

from drive.models import create_indices
from drive.filters import DuckDBFilter, DuckdbTemplate, filter_ibd_file
from drive.helper_funcs import split_target_string

logger = CustomLogger.get_logger(__name__)


class NetworkIDNotFound(Exception):
    def __init__(self, network_id: str) -> None:
        self.msg = f"The id, {network_id}, was not found in the IBD data. Make sure that the ID you are looking for perfectly matches what should be in the DRIVE file. Trailing zeros can make a difference, 10.0 != 10 in DRIVE."
        super().__init__(self.msg)


def check_kwargs(args_dict: dict[str, Any]) -> str | None:
    """Function that will make sure that the necessary arguments are passed to distance function

    Parameters
    ----------
    args_dict : Dict[str, Any]
        Dictionary that has the arguments as keys and the values for the distance function
    """
    if not all(
        [
            elem in args_dict.keys()
            for elem in ["pair_1", "pair_2", "pairs_df", "cm_threshold"]
        ]
    ):
        return "Not enough arguments passed to the _determine_distances function. \
            Expected pair_1, pair_2, pairs_df, cm_threshold"


def _determine_distances(**kwargs) -> tuple[str | None, float]:
    """Function that will determine the distances between the main grid and then \
        each connected grid. It will use the min cM value divided in half for all \
        grids that don't share a segment.

    Parameters
    ----------
    pair_1 : str
        string that has the main grid id


    pairs_df : pd.DataFrame
        dataframe from the pairs file that has been filtered to just connections \
            with the main grid
    """
    # checking to make sure the function has the right parameters in the kwargs and then
    # returning an error if it doesn't
    err = check_kwargs(kwargs)

    if err is not None:
        return err, 0.0

    # getting all the necessary values out of the kwargs dict
    pair_1 = kwargs.pop("pair_1")
    pair_2 = kwargs.pop("pair_2")
    pairs_df = kwargs.pop("pairs_df")
    min_cM = kwargs.pop("cm_threshold")

    if pair_2 == pair_1:
        return None, float(0)

    # pulling out the length of the IBD segment based on hapibd
    filtered_pairs: pd.DataFrame = pairs_df[
        ((pairs_df["pair_1"] == pair_1) & (pairs_df["pair_2"] == pair_2))
        | ((pairs_df["pair_1"] == pair_2) & (pairs_df["pair_2"] == pair_1))
    ]

    if filtered_pairs.empty:
        ibd_length: float = min_cM / 2

    else:
        ibd_length: float = filtered_pairs.iloc[0]["length"]

    return None, 1 / ibd_length


def record_matrix(output: Path | str, matrix, pair_list: list[str]) -> None:
    """Function that will write the distance matrix to a file

    Parameters
    ----------
    output : str
        filepath to write the output to

    matrix : array
        array that has the distance matrix for each individual

    pair_list : List[str]
        list of ids that represent each row of the pair_list

    Raises
    ------
    AssertionError
        raises an AssertionError if the pair_list has no values in it because this means no individuals were identified within the pair_list
    """
    assert (
        len(pair_list) != 0
    ), "There were no pairs recorded into the pair list. This error likely means there is a bug within the make_distance_matrix_function."

    with open(output, "w") as output_file:
        for i in range(len(pair_list)):
            distance_str = "\t".join([str(distance) for distance in matrix[i]])
            output_file.write(f"{pair_list[i]}\t{distance_str}\n")


@dataclass
class DistanceMatrixResults:
    distance_matrix_id_mapping: list[str]
    distance_matrix: npt.NDArray
    id_mapping: dict[str, str] = field(default_factory=dict)


def make_distance_matrix(
    pairs_df: pl.DataFrame,
    min_cM: int,
    map_ids: bool,
    distance_function: Callable = _determine_distances,
) -> DistanceMatrixResults:
    """Function that will make the distance matrix

    Parameters
    ----------
    pairs_df : pl.DataFrame
        dataframe that has the pairs_files. it should have at least three columns
        called 'pair_1', 'pair_2', and 'length'

    min_cM : float
        This is the minimum centimorgan threshold that will be divided in half to
        get the ibd segment length when pairs do not share a segment

    map_ids : bool
        Boolean indicating whether we want to map the ids to a random mapping or not

    Returns
    -------
    DistanceMatrixResults
        returns a dataclass where the first object is a list of ids that has the
        individual id that corresponds to each row. The second object is the
        distance matrix
    """

    id_mapping_df = (
        pl.concat(
            [
                pairs_df.select(pl.col("pair_1").alias("ID")),
                pairs_df.select(pl.col("pair_2").alias("ID")),
            ]
        )
        .unique()
        .with_row_index("ID_mapping", offset=1)
    )

    # We need to pull out the list of ids to use in the analysis
    if map_ids:
        id_list = id_mapping_df.get_column("ID_mapping").to_list()
        id_mapping: dict[str, str] = dict(
            zip(
                id_mapping_df.get_column("ID_mapping"),
                id_mapping_df.get_column("ID"),
            )
        )
    else:
        id_list = id_mapping_df.get_column("ID").to_list()
        id_mapping = {}

    matrix = zeros((len(id_list), len(id_list)), dtype=float)

    ids_index = []

    for i in range(len(id_list)):
        ids_index.append(id_list[i])

        for j in range(len(id_list)):
            err, distance = distance_function(
                pair_1=id_list[i],
                pair_2=id_list[j],
                pairs_df=pairs_df.to_pandas(),
                cm_threshold=min_cM,
            )
            if err is not None:
                logger.critical(err)
                return DistanceMatrixResults([], None, {})

            matrix[i][j] = distance

    return DistanceMatrixResults(ids_index, matrix, id_mapping)


def generate_dendrogram(matrix: npt.NDArray) -> npt.NDArray:
    """Function that will perform the hierarchical clustering algorithm

    Parameters
    ----------
    matrix : Array
        distance matrix represented by 2D numpy array.
        distance should be calculated based on 1/(ibd segment
        length)

    Returns
    -------
    Array
        returns the results of the clustering as a numpy array
    """
    squareform_matrix = squareform(matrix)

    return sch.linkage(squareform_matrix, method="ward")


# def _check_for_overlap(cases: List[str], exclusions: List[str]) -> None:
#     """Make sure there is no overlap between individuals in the cases and exclusions \
#         list provided to the _generate_label_colors method

#     Parameters
#     ----------
#     cases : List[str]
#         list of individuals who are considered cases for a
#         disease or phenotype

#     exclusions : List[str]
#         list of individuals who are consider exclusions and are indicated as N/A or
#         -1 by the phenotype file. This value defaults to None.

#     Raises
#     ------
#     ValueError
#         If there are overlapping individuals in the cases and exclusions lists then a \
#             ValueError is raised to indicate that the user should check their labelling.
#     """
#     if [ind for ind in cases if ind in exclusions]:
#         raise ValueError(
#             "Overlapping individuals found between cases and exclusions \
#                         lists. Please check your case and exclusions list labelling."
#         )


# def _generate_label_colors(
#     grid_list: List[str], cases: List[str], exclusions: List[str] = []
# ) -> Dict[str, str]:
#     """Function that will generate the color dictionary
#     indicating what color each id label should be

#     Parameters
#     ----------
#     grid_list : list[str]
#         list of id strings

#     cases : List[str]
#         list of individuals who are considered cases for a
#         disease or phenotype

#     exclusions : List[str]
#         list of individuals who are consider exclusions and are indicated as N/A or
#         -1 by the phenotype file. This value defaults to None

#     Returns
#     -------
#     dict[str,str]
#         returns a dictionary where the key is the id and the
#         values are the color of the label for that id.
#     """

#     if exclusions:
#         _check_for_overlap(cases, exclusions)

#     color_dict = {}

#     for grid in grid_list:
#         if grid in cases:
#             color_dict[grid] = "r"
#         elif grid in exclusions:
#             color_dict[grid] = "g"
#         else:
#             color_dict[grid] = "k"

#     return color_dict


def draw_dendrogram(
    clustering_results: npt.NDArray,
    grids: list[str],
    output_name: Path | str,
    title: str | None = None,
    node_font_size: int = 10,
) -> tuple[plt.Figure, plt.Axes, dict[str, Any]]:
    """Function that will draw the dendrogram

    Parameters
    ----------
    clustering_results : npt.NDArray
        numpy array that has the results from running the generate_dendrogram function

    grids : list[str]
        list of ids to use as labels

    output_name : Path | str
        path object or a string that tells where the
        dendrogram will be saved to.

    # cases : list[str] | None
    #     list of case ids. If the user doesn't provide this
    #     value then all of the labels on the dendrogram will
    #     be black. If the user provides a value then the case
    #     labels will be red. Value defaults to None

    # exclusions : List[str]
    #     list of individuals who are considered exclusions and are
    #     indicated as N/A or -1 by the phenotype file. This value
    #     defaults to None

    title : str | None
        Optional title for the plot. If this is not provided
        then the plot will have no title

    node_font_size : int
        Size for the font of the dendrogram leaf nodes

    Returns
    -------
    tuple[plt.Figure, plt.Axes, dict[str, Any]]
        returns a tuple with the matplotlib Figure, the
        matplotlib Axes object, and a dictionary from the sch.dendrogram
        command
    """
    figure = plt.figure(figsize=(15, 12))
    ax = plt.subplot(111)

    # Temporarily override the default line width:
    with plt.rc_context(
        {
            "lines.linewidth": 2,
        }
    ):
        dendrogram = sch.dendrogram(
            clustering_results,
            labels=grids,
            orientation="left",
            color_threshold=0,
            above_threshold_color="black",
            leaf_font_size=node_font_size,
        )

    # change the color of the nodes for cases if the user wants to.

    # # remove whitespace from the case labels
    # cases = [case.strip() for case in cases]

    # if cases:
    #     color_dict = _generate_label_colors(grids, cases, exclusions)
    #     yaxis_labels = ax.get_ymajorticklabels()
    #     for label in yaxis_labels:
    #         label.set_color(color_dict[label.get_text()])

    # removing the ticks and axes
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.axes.get_xaxis().set_visible(False)

    if title:
        plt.title(title, fontsize=20)

    plt.savefig(output_name)

    return figure, ax, dendrogram


def load_networks(
    drive_results: Path,
    max_network_size: int,
    min_network_size: int,
    network_id: str | None = None,
) -> dict[str, dict[str, list[str]]]:
    """method reads the drive networks into a dictionary. If the user chooses to
    generate dendrograms for all the networks then DRIVE only returns those
    networks that are between a certain size range

    Parameters
    ----------
    drive_results : Path
        output file from running the clustering step of DRIVE

    max_network_size : int
        the maximum size of a network that will be allowed in the analysis.
        Drawing large networks well is hard to automate. The default value is 30

    min_network_size : int
        minimum size of a network to draw. Drawing 2 person networks makes no
        sense so by default DRIVE only draws dendrograms for networks of 3 or
        more people. Users can choose a different value if they wish.

    network_id : str
        the id of the cluster ID by DRIVE. Default value = none

    Returns
    -------
    dict[str, list[str]]
        returns a dictionary where the keys are the cluster IDs and the values
        are a list of haplotypes in the cluster

    Raises
    ------
    NetworkIDNotFound
        raises a KeyError if the network_id value is not found in the drive file
    """
    return_dict = {}

    with open(drive_results, "r", encoding="utf-8") as drive_file:
        logger.verbose(
            f"Identifying network {network_id} within the DRIVE output, {drive_results}"
        )
        if network_id:
            for line in drive_file:
                (
                    clst_id,
                    network_size,
                    haplotype_count,
                    edge_count,
                    connectedness,
                    _,
                    id_list,
                    haplotype_list,
                    *_,
                ) = line.strip().split("\t")
                if clst_id == network_id:
                    return_dict[clst_id] = {
                        "ids": id_list.strip().split(","),
                        "haplotypes": haplotype_list.strip().split(","),
                    }

            if not return_dict:
                logger.critical(
                    f"The id {network_id} was not found within the DRIVE file at {drive_file}."
                )
                raise NetworkIDNotFound(network_id)
        else:
            logger.verbose(
                "No network id passed to program. Reading in data for all of the networks identified by DRIVE."
            )
            logger.verbose(
                f"For the sake of drawing efficiency, only gathering dendrograms that are between size {min_network_size} and {max_network_size}"
            )

            for line in drive_file:
                # we can skip the header line
                if "clstID" in line:
                    pass
                else:
                    (
                        clst_id,
                        network_size,
                        haplotype_count,
                        edge_count,
                        connectedness,
                        _,
                        id_list,
                        haplotype_list,
                        *_,
                    ) = line.strip().split("\t")
                    if min_network_size <= len(id_list.split(",")) <= max_network_size:
                        return_dict[clst_id] = {
                            "ids": id_list.strip().split(","),
                            "haplotypes": haplotype_list.strip().split(","),
                        }

    logger.debug(f"Stored {len(return_dict.keys())} networks within the dictionary")

    return return_dict


def generate_dendrograms(args) -> None:
    # Need to read in the drive networks to get the appropriate ids
    network_ids = load_networks(
        args.input, args.max_network_size, args.min_network_size, args.network_id
    )
    # generate an object that has all of the indices for the correct ibd format
    indices = create_indices(args.format.lower())

    ##target gene region or variant position
    target_gene = split_target_string(args.target)

    # Lets load the segment data into memory
    segment_filter = DuckDBFilter(indices, target_gene, args.segment_overlap)

    sql_query = DuckdbTemplate(
        ibd_segment_file=args.ibd,
        filterObj=segment_filter,
        indices=indices,
        min_cm=args.min_cm,
    ).get_network_filter(add_sample_filter=False)

    filtered_ibd_df = filter_ibd_file(
        sql_query=sql_query, keep_df=pl.DataFrame(), indices=indices
    )
    # At this point in the code the filtered_ibd_df has columns for the id1 & id2 string, the chromosome, start and end position of the segment, cm length, and hapid1 & hapid2.

    for clstID, id_dict in network_ids.items():
        # generate output path for the dendrogram image
        logger.info(f"generating dendrogram for network {clstID}")
        args.output.mkdir(parents=True, exist_ok=True)

        full_output_path = args.output / f"network_{clstID}_dendrogram.png"

        haplotype_list = id_dict["haplotypes"]

        network_ibd_df = (
            filtered_ibd_df.filter(
                pl.col("hapid1").is_in(haplotype_list),
                pl.col("hapid2").is_in(haplotype_list),
            )
            .rename(
                {
                    indices.id1_indx: "pair_1",
                    indices.id2_indx: "pair_2",
                    indices.cM_indx: "length",
                }
            )
            .select(pl.col(["pair_1", "pair_2", "length"]))
        )

        distanceMatrixObj = make_distance_matrix(
            network_ibd_df,
            args.min_cm,
            args.map_ids,
        )

        if distanceMatrixObj.id_mapping:
            with open(
                args.output / f"network_{clstID}_id_mapping.txt", "w", encoding="utf-8"
            ) as mapping_fh:
                mapping_fh.write("Original_ID\tMapped_ID\n")
                for orig_id, new_id in distanceMatrixObj.id_mapping.items():
                    mapping_fh.write(f"{orig_id}\t{new_id}\n")

        if args.keep_temp:
            temp_dir = args.output / f"network_{clstID}_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)

            full_output_matrix_path = temp_dir / f"network_{clstID}_distance_matrix.txt"

            logger.info(
                f"recorded the distance matrix to the following path: {full_output_matrix_path}"
            )

            record_matrix(
                full_output_matrix_path,
                distanceMatrixObj.distance_matrix,
                distanceMatrixObj.distance_matrix_id_mapping,
            )

        dendrogram_array = generate_dendrogram(distanceMatrixObj.distance_matrix)

        logger.info(f"writing the output dendrogram to {full_output_path}")

        _ = draw_dendrogram(
            dendrogram_array,
            distanceMatrixObj.distance_matrix_id_mapping,
            full_output_path,
            args.title,
            args.font_size,
        )
