import logging
from pandas import DataFrame
from igraph import Graph, VertexClustering
from drive.models.types import ClusterConfig, Metrics


from drive.network.graph.metrics import (
    identify_false_positive_edges,
    identify_true_positive_edges,
)
from log import CustomLogger

# creating a logger
logger: logging.Logger = CustomLogger.get_logger(__name__)


def generate_graph(
    ibd_edges: DataFrame,
    ibd_vertices: DataFrame | None = None,
) -> Graph:
    """Method that will be responsible for creating the graph
    used in the network analysis

    Parameters
    ----------
    ibd_edges : DataFrame
        DataFrame that has the edges of the graph with the length
        of the edges.

    ibd_vertices : Optional[DataFrame]
        DataFrame that has information for each vertex in the
        graph. This value will be none when we are redoing the clustering
    """
    if ibd_vertices is not None:
        logger.debug("Generating graph with vertex labels.")
        return Graph.DataFrame(
            ibd_edges, directed=False, vertices=ibd_vertices, use_vids=False
        )

    else:
        logger.debug(
            "No vertex metadata provided. Vertex ids will be nonnegative integers"
        )
        # return ig.Graph.DataFrame(ibd_edges, directed=False, use_vids=False)
        return Graph.DataFrame(ibd_edges, directed=False)


def random_walk(graph: Graph, config: ClusterConfig) -> VertexClustering:
    """Method used to perform the random walk from igraph.community_walktrap

    Parameters
    ----------
    graph : ig.Graph
        graph object created by ig.Graph.DataFrame

    Returns
    -------
    ig.VertexClustering
        result of the random walk cluster. This object has
        information about clusters and membership
    """
    logger.debug(
        f"Performing the community walktrap algorithm with a random walk step size of: {config.random_walk_step_size}"
    )

    ibd_walktrap = Graph.community_walktrap(
        graph, weights="cm", steps=config.random_walk_step_size
    )

    random_walk_clusters = ibd_walktrap.as_clustering()

    logger.verbose(random_walk_clusters.summary())

    return random_walk_clusters


def gather_members(
    random_walk_members: list[int], clst_id: int, graph: Graph
) -> tuple[list[int], list[int]]:
    """Generate a list of individual ids in the network

    Parameters
    ----------
    random_walk_members : list[int]
        list of all members from the random walk results

    clst_id : int
        id for the cluster. This value is used to pull out members
        that belong to the cluster

    graph : ig.Graph
        Graph object formed by ig.Graph.DataFrame

    Returns
    -------
    tuple[list[int], list[int]]
        returns a list of ids of individuals in the network and then
        a list of vertex ids. The individual ids are just the index
        of the element in the membership list and the vertex ids are
        the list of ids provided by name label in the vs() property.
    """
    member_list = []
    # this list has the ids. It is sometimes the same as the
    # member_list but it will not be the same in the redo_networks
    # graph
    vertex_ids = []

    for member_id, assigned_clst_id in enumerate(random_walk_members):
        if assigned_clst_id == clst_id:
            member_list.append(graph.vs()[member_id]["name"])
            vertex_ids.append(member_id)

    return member_list, vertex_ids


def get_network_haplotypes_and_members(
    members: list[int], haplotype_mappings: dict[int, str]
) -> tuple[list[str], set[str]]:
    """remap the haplotype integer ids back to the haplotype
    strings for the output file

    Parameters
    ----------
    members : list[int]
        list of integers that represent the name of each vertex in the network
        corresponding to the graph

    Returns
    -------
    Tuple[List[str], List[str]]
        returns a list of haplotype id strings in the network. These
        strings include the phase number. Also returns a list of ids
        within the networks. This will be the same as the haplotype
        id without the phase number
    """
    haplotypes = [haplotype_mappings[value] for value in members]

    member_ids = {value[:-2] for value in haplotypes}

    return haplotypes, member_ids


def hub_detection(
    members: list[int], edges_df: DataFrame, config: ClusterConfig
) -> list[int]:
    """Method that will be use to perform the hub detection"""
    # creates an empty dataframe with these columns
    clst_conn = DataFrame(columns=["idnum", "conn", "conn.N", "TP"])
    # iterate over each member id
    # for idnum in network.haplotypes:

    for idnum in sorted(list(members)):
        conn = sum(
            list(
                map(
                    lambda x: 1 / x,
                    edges_df.loc[
                        (edges_df["idnum1"] == idnum) | (edges_df["idnum2"] == idnum)
                    ]["cm"],
                )
            )
        )
        conn_idnum = list(edges_df.loc[(edges_df["idnum1"] == idnum)]["idnum2"]) + list(
            edges_df.loc[(edges_df["idnum2"] == idnum)]["idnum1"]
        )
        conn_tp = len(
            edges_df.loc[
                edges_df["idnum1"].isin(conn_idnum)
                & edges_df["idnum2"].isin(conn_idnum)
            ].index
        )

        # assert 1 == 0
        if len(conn_idnum) == 1:
            connTP = 1
        else:
            try:
                connTP = conn_tp / (len(conn_idnum) * (len(conn_idnum) - 1) / 2)
            except ZeroDivisionError:
                raise ZeroDivisionError(
                    f"There was a zero division error encountered when looking at the network with the id {idnum}"  # noqa: E501
                )  # noqa: E501

        clst_conn.loc[idnum] = [idnum, conn, len(conn_idnum), connTP]
    rmID = list(
        clst_conn.loc[
            (clst_conn["conn.N"] > (config.segment_dist_threshold * len(members)))
            & (clst_conn["TP"] < config.min_connected_threshold)
            & (
                clst_conn["conn"]
                > sorted(clst_conn["conn"], reverse=True)[
                    int(config.hub_threshold * len(members))
                ]
            )
        ]["idnum"]
    )

    return rmID


def get_cluster_metrics(
    cluster: Graph,
    clst_id: int,
    members: list[int],
    random_walk_clusters: VertexClustering,
    vertex_ids: list[int],
) -> Metrics:

    # Next we get the number of edges/ ratio of actual edges to
    # the potential edges
    (
        true_pos_count,
        true_pos_ratio,
    ) = identify_true_positive_edges(members, clst_id, random_walk_clusters)
    # next we determine the number of false positive edges

    false_neg_list = identify_false_positive_edges(cluster, vertex_ids)

    return Metrics(
        tp_count=true_pos_count,
        tp_ratio=true_pos_ratio,
        fp_count=len(false_neg_list),
    )
