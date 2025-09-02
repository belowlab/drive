About DRIVE
===========
DRIVE (Distant Relatedness for Identification and Variant Evaluation) is a CLI tool that efficiently leverages graph theory algorithms and IBD in large-scale cohorts to identify networks of individuals with shared haplotypes at a specified locus. These graph approaches allows for DRIVE to aggregate the pairwise shared IBD segments information into networks while retaining the identity of the pairwise segments.

DRIVE utilizes common software design patterns to allow for adaption into custom analytical pipelines and to allow for adoption into a variety of computational platforms, including cloud computing environments. To allow for this adaptability, DRIVE implements a plugin architecture so that that the user can specify which plugins they wish to run and they can design their own plugins. The following paragraph describes the algorithm behind DRIVE.

DRIVE Haplotype Clustering (Through the cluster subcommand)
-----------------------------------------------------------
DRIVE first filters the provided IBD inputs to those segments overlapping the provided target locus and to those segments longer than a user-provided minimum segment length threshold. By default, this threshold is set to 3 cM. A graph of the data is then constructed where each participant’s phased haplotype is a vertex, and each edge represents a shared IBD segment. DRIVE uses an iterative process to traverse this graph and identify networks. This graph is first traversed using a community walktrap algorithm, as described by Pons and Latapy `(article) <https://arxiv.org/abs/physics/0512106>`_, where the segment length is used as a probability weight. This algorithm relies on a series of random walks to calculate similarity between vertices in the graph. Similar vertices are ultimately aggregated into “communities”. In the paper, Pons et al. reported that this algorithm has a worst-case O(mn :sup:`2`) runtime and O(n :sup:`2`) memory usage although in most cases the runtime should be O(n :sup:`2` logn) and the memory space should be O(n :sup:`2`). 

To reduce identification of spurious large networks connected by very small segments, the size and connectedness of each network are calculated, where connectedness is defined as the proportion of edges in the graph compared to the number of total possible edges. Based on these measurements, large networks or sparsely connected networks iteratively go through a refinement process that mimics the original traversal where a new graph is created consisting of only the limited vertices in the network. By default, DRIVE performs this refinement for networks that are larger than 30 participants and those where the connectedness is less than 50%. If the additional random walk fails to break up the original network, DRIVE then performs a hub detection algorithm that calculates how many edges each node has and generates scores for each node by summing the inverse IBD segment length for every pairwise segment involving that node. Nodes are then classified as hubs if they meet the following three criteria: 

1) nodes connected to a substantial proportion of others in the network (default: 20% of network size)
2) nodes that are sparsely connected (default: 50%) 
3) nodes with scores greater than the tail of the network distribution (default: 1% of scores) 

These hub nodes are removed from the graph all at once and another random walk is performed.  This refinement process will repeat until all networks meet the provided size and sparsity requirements, or the number of iterations exceeds the provided limit. At most, each participant will end up in two networks, one for each phased haplotype.

Enrichment Test
---------------
If a phenotype file is provided as input, then after DRIVE has identified networks, a phenotypic enrichment test will also be performed using binomial statistics. Since only networks containing at least two phenotype cases are tested, one participant who is a phenotype case is considered a proband for each network and is dropped from the following calculation. The  phenotype frequency within each network is then compared to the frequency within the entire cohort to generate an empirical p-value.

This algorithm for DRIVE is depicted in the following figure.


.. figure:: /assets/images/DRIVE_flowchart_4_27_25.excalidraw.png
    :height: 500
    :figwidth: 500
    :align: center
    
    Flowchart describing the DRIVE algorithm and decisions that affect runtime behavior. *generated using excalidraw*


DRIVE dendrogram subcommand:
----------------------------
DRIVE provides as basic implementation of dendrograms that allows the user to visualize the genetic distance between individuals in a phylogenetic tree. This figures illustrates the local IBD sharing that is present in the network. This functionality is implemented using the python library Scipy specific the linkage function using the "ward" linkage algorithm. The user can generate the dendrogram using the DRIVE subcommand "dendrogram". 


