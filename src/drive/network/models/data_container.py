from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Any

from .networks import Network_Interface


@dataclass
class RuntimeState:
    """main class to hold the data from the network analysis and the different pvalues"""

    networks: List[Network_Interface]
    output_path: Path
    carriers: Dict[str, Dict[str, Set[str]]]
    phenotype_descriptions: Dict[str, Dict[str, str]]
    config_options: dict[str, Any] = field(default_factory=dict)
