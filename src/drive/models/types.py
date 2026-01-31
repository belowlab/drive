# File will have different Interfaces used in the program as well as different classes for types. This will simplify the imports and allow me to reduce coupling between modules

from collections import namedtuple
from dataclasses import dataclass

# namedtuple that will contain information about the gene being run
Genes = namedtuple("Genes", ["chr", "start", "end"])


@dataclass(slots=True, frozen=True)
class Metrics:
    tp_count: int
    tp_ratio: float
    fp_count: int


@dataclass
class ClusterConfig:
    min_connected_threshold: float
    max_network_size: int
    max_recheck_count: int
    random_walk_step_size: int
    min_cluster_size: int
    segment_dist_threshold: float
    hub_threshold: float
    recluster: bool


@dataclass(slots=True)
class NetworkCandidate:
    member_ids: list[int]
    curr_iteration: int
    candidate_id: str
    candidate_metrics: Metrics
