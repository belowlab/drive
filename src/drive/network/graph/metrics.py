from igraph import Graph, VertexClustering
import itertools


def identify_false_positive_edges(graph: Graph, vertex_list: list[int]) -> list[int]:
    """determine the number of false positive edges

    Parameters
    ----------
    graph : ig.Graph
        graph object returned from ig.Graph.DataFrame

    vertex_list : List[int]
        list of vertex ids within the specific network

    Returns
    -------
    Tuple[int, List[int]]
        returns a tuple where the first element is the
        number of edges in the graph and the second
        element is a list of false positive edges.
    """
    all_edge = set([])

    for mem in vertex_list:
        all_edge = all_edge.union(set(graph.incident(mem)))

    false_negative_edges = list(
        all_edge.difference(
            list(
                graph.get_eids(
                    pairs=list(itertools.combinations(vertex_list, 2)),
                    directed=False,
                    error=False,
                )
            )
        )
    )
    return false_negative_edges


def identify_true_positive_edges(
    member_list: list[int], clst_id: int, random_walk_results: VertexClustering
) -> tuple[int, float]:
    """determining the number of true positive edges

    Parameters
    ----------
    member_list : List[int]
        list of ids within the specific network

    clst_id : int
        id for the original cluster

    random_walk_results : ig.VertexClustering
        vertexClustering object returned after the random
        walk that has the different clusters

    Returns
    -------
    Tuple[int, float]
        returns a tuple where the first element is the
        number of edges in the graph and the second
        element is the ratio of actual edges in the
        graph compared to the theoretical maximum number
        of edges in the graph.
    """
    # getting the total number of edges possible
    theoretical_edge_count = len(list(itertools.combinations(member_list, 2)))

    # Getting the number of edges within the graph and saving it
    # as a dictionary key, 'true_positive_n'
    cluster_edge_count = len(random_walk_results.subgraph(clst_id).get_edgelist())

    return cluster_edge_count, cluster_edge_count / theoretical_edge_count
