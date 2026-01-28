import logging
from pandas import DataFrame
from igraph import Graph, VertexClustering
from drive.models.types import ClusterConfig


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
