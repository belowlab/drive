from pathlib import Path
import pandas as pd
from typing import Callable, Any, Dict, List, Optional, Union
from numpy import zeros
import numpy.typing as npt
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt


def gather_individuals_from_input() -> dict:
    ...


def check_kwargs(args_dict: dict[str, Any]) -> Optional[str]:
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


def _determine_distances(**kwargs) -> tuple[Optional[str], float]:
    """Function that will determine the distances between the main grid and then \
        each connected grid. It will use a value of 2.5 for all grids that don't \
            share a segment. This is just the min cM value, 5cM, divided in half

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

    if err != None:
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

        # print(
        #     f"no pairwise sharing for grids {pair_1} and {pair_2}. Using an ibd length of {ibd_length}cM instead"
        # )

    else:
        ibd_length: float = filtered_pairs.iloc[0]["length"]

    return None, 1 / ibd_length


def record_matrix(output: Union[Path, str], matrix, pair_list: List[str]) -> None:
    """Function that will write the dataframe to a file

    Parameters
    ----------
    output : str
        filepath to write the output to

    matrix : array
        array that has the distance matrix for each individual

    pair_list : List[str]
        list of ids that represent each row of the pair_list
    """

    with open(output, "w") as output_file:
        for i in range(len(pair_list)):
            distance_str = "\t".join([str(distance) for distance in matrix[i]])
            output_file.write(f"{pair_list[i]}\t{distance_str}\n")


def make_distance_matrix(
    pairs_df: pd.DataFrame,
    min_cM: int,
    distance_function: Callable = _determine_distances,
) -> tuple[list[str] | None, npt.NDArray]:
    """Function that will make the distance matrix

    Parameters
    ----------
    pairs_df : pd.DataFrame
        dataframe that has the pairs_files. it should have at least three columns
        called 'pair_1', 'pair_2', and 'length'

    min_cM : float
        This is the minimum centimorgan threshold that will be divided in half to
        get the ibd segment length when pairs do not share a segment

    Returns
    -------
    Dict[str, Dict[str, float]]
        returns a tuple where the first object is a list of ids that has the
        individual id that corresponds to each row. The second object is the
        distance matrix
    """
    # get a list of all the unique ids in the pairs_df
    id_list: list[str] = list(
        set(pairs_df.pair_1.values.tolist() + pairs_df.pair_2.values.tolist())
    )

    matrix = zeros((len(id_list), len(id_list)), dtype=float)

    ids_index = []

    for i in range(len(id_list)):
        ids_index.append(id_list[i])

        for j in range(len(id_list)):
            err, distance = distance_function(
                pair_1=id_list[i],
                pair_2=id_list[j],
                pairs_df=pairs_df,
                cm_threshold=min_cM,
            )
            if err != None:
                print(err)
                return None, None

            matrix[i][j] = distance

    return ids_index, matrix


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


def _check_for_overlap(cases: List[str], exclusions: List[str]) -> None:
    """Make sure there is no overlap between individuals in the cases and exclusions \
        list provided to the _generate_label_colors method

    Parameters
    ----------
    cases : List[str]
        list of individuals who are considered cases for a
        disease or phenotype

    exclusions : List[str]
        list of individuals who are consider exclusions and are indicated as N/A or
        -1 by the phenotype file. This value defaults to None.

    Raises
    ------
    ValueError
        If there are overlapping individuals in the cases and exclusions lists then a \
            ValueError is raised to indicate that the user should check their labelling.
    """
    if [ind for ind in cases if ind in exclusions]:
        raise ValueError(
            "Overlapping individuals found between cases and exclusions \
                        lists. Please check your case and exclusions list labelling."
        )


def _generate_label_colors(
    grid_list: List[str], cases: List[str], exclusions: List[str] = []
) -> Dict[str, str]:
    """Function that will generate the color dictionary
    indicating what color each id label should be

    Parameters
    ----------
    grid_list : list[str]
        list of id strings

    cases : List[str]
        list of individuals who are considered cases for a
        disease or phenotype

    exclusions : List[str]
        list of individuals who are consider exclusions and are indicated as N/A or
        -1 by the phenotype file. This value defaults to None

    Returns
    -------
    dict[str,str]
        returns a dictionary where the key is the id and the
        values are the color of the label for that id.
    """

    if exclusions:
        _check_for_overlap(cases, exclusions)

    color_dict = {}

    for grid in grid_list:
        if grid in cases:
            color_dict[grid] = "r"
        elif grid in exclusions:
            color_dict[grid] = "g"
        else:
            color_dict[grid] = "k"

    return color_dict


def draw_dendrogram(
    clustering_results: npt.NDArray,
    grids: List[str],
    output_name: Union[Path, str],
    cases: Optional[List[str]] = None,
    exclusions: List[str] = [],
    title: Optional[str] = None,
    node_font_size: int = 10,
    save_fig: bool = False,
) -> tuple[plt.Figure, plt.Axes, Dict[str, Any]]:
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

    cases : list[str] | None
        list of case ids. If the user doesn't provided this
        value then all of the labels on the dendrogram will
        be black. If the user provides a value then the case
        labels will be red. Value defaults to None

    exclusions : List[str]
        list of individuals who are consider exclusions and are
        indicated as N/A or -1 by the phenotype file. This value
        defaults to None

    title : str | None
        Optional title for the plot. If this is not provided
        then the plot will have no title

    node_font_size : int
        Size for the font of the dendrogram leaf nodes

    save_fig : bool
        whether or not to save the figure. Defaults to False.

    Returns
    -------
    tuple[plt.Figure, plt.Axes, dict[str, Any]]
        returns a tuple with the matplotlib Figure, the
        matplotlib Axes object, and a dictionary from the sch.
        dendrogram command
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

    # remove whitespace from the case labels
    cases = [case.strip() for case in cases]

    if cases:
        color_dict = _generate_label_colors(grids, cases, exclusions)
        yaxis_labels = ax.get_ymajorticklabels()
        for label in yaxis_labels:
            label.set_color(color_dict[label.get_text()])

    # removing the ticks and axes
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.axes.get_xaxis().set_visible(False)

    if title:
        plt.title(title, fontsize=20)
    if save_fig:
        plt.savefig(output_name)

    return figure, ax, dendrogram


def generate_dendrograms(args) -> None:
    ...
