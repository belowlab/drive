# File will have different Interfaces used in the program as well as different class for types. This will simplify the imports and allow me to reduce coupling between modules

from collections import namedtuple
from dataclasses import dataclass, field
from typing import Protocol

from pandas import DataFrame

# namedtuple that will contain information about the gene being run
Genes = namedtuple("Genes", ["chr", "start", "end"])


# Interface to represent the network object
class Network_Interface(Protocol):
    clst_id: float  # I don't like this attribute being a float but for now it has to remain this way for backwards compatibility
    true_positive_count: int
    true_positive_percent: float
    false_negative_edges: list[int]
    false_negative_count: int
    members: set[int]
    haplotypes: list[int]
    min_pvalue_str: str = ""
    pvalues: dict[str, str] = field(default_factory=dict)

    def print_members_list(self) -> str:
        """Returns a string that has all of the members ids separated by space

        Returns
        -------
        str
            returns a string where the members list attribute
            is formatted as a string for the output file. Individuals strings are joined by comma.
        """
        ...


# interface for the filter object
@dataclass
class Filter(Protocol):
    ibd_vs: DataFrame = field(default_factory=DataFrame)
    ibd_pd: DataFrame = field(default_factory=DataFrame)


# This variable will represent our return type from the clustering
NetworkResults = dict[list[str], list[Network_Interface]]
