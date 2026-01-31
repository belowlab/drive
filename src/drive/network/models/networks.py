from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar

T = TypeVar("T", bound="Network")


class Network_Interface(Protocol):
    clst_id: str
    true_positive_count: int
    true_positive_percent: float
    false_negative_count: int
    members: set[int] | set[str]
    haplotypes: list[int] | list[str]
    min_pvalue_str: str = ""
    pvalues: dict[str, dict[str, Any]] = field(default_factory=dict)

    def print_members_list(self) -> str:
        """Returns a string that has all of the member IDs separated by a comma

        Returns
        -------
        str
            returns a string where the members list attribute
            is formatted as a string for the output file. Individual strings are joined by comma.
        """
        ...


@dataclass
class Network:
    clst_id: str
    true_positive_count: int
    true_positive_percent: float
    false_negative_count: int
    members: set[int] | set[str]
    haplotypes: list[int] | list[str]
    min_pvalue_str: str = ""
    pvalues: dict[str, dict[str, Any]] = field(default_factory=dict)

    def print_members_list(self) -> str:
        """Returns a string that has all of the member IDs separated by a comma

        Returns
        -------
        str
            returns a string where the members list attribute
            is formatted as a string for the output file. Individual strings are joined by comma.
        """
        return ", ".join(list(map(str, self.members)))

    def __lt__(self, comp_class: Network_Interface) -> bool:
        """Override the less than method so that objects can be sorted in
        ascending numeric order based on cluster id.

        Parameters
        ----------
        comp_class : Network
            Network object to compare.

        Returns
        -------
        bool
            returns True if the self cluster id is less than the
            comp_class cluster id.
        """

        return self.clst_id < comp_class.clst_id
