from pathlib import Path
from dataclasses import dataclass, field
import csv
import sys

from log import CustomLogger

from pandas import read_csv

logger = CustomLogger.get_logger(__name__)


@dataclass
class PhecodesMapper:
    phecode_names: dict[str, str] = field(default_factory=dict)
    category_groups: dict[str, list[str]] = field(default_factory=dict)


def validate_header(header_str: list[str]) -> None:
    """Ensures that the file has the columns we expect and they are in the right order

    Parameters
    ----------
    header_str
        first line of the phecode descriptions file. This files are found in the 'phecode_mappings' folder

    Raises
    ------
    ValueError
        raises a ValueError if the header string is the
        wrong size and if it doesn't have the expect columns
        in the expected order
    """

    if len(header_str) != 3:
        err_str = f"expected the phecode mapping file to have 3 columns: phecode, phecode_string, and category. Instead found {len(header_str)} columns"
        logger.fatal(err_str)
        raise ValueError(err_str)
    if (
        header_str[0] != "phecode"
        or (header_str[1] != "phecode_string" and header_str[1] != "phenotype")
        or header_str[2] != "category"
    ):
        err_str = f"expected the order of the columns to be 'phecode, phecode_string, category' instead the order was '{header_str[0]} {header_str[1]} {header_str[2]}'"
        logger.fatal(err_str)
        raise ValueError(err_str)


def load_phenotype_descriptions(
    phecode_container: PhecodesMapper, phecode_filepaths: Path
) -> None:
    """Function that will loads information about the phecode id names and the categories into a dictionary

    Parameters
    ----------
    phecode_container : PhecodesMapper
        class that contains 2 maps. One map has key value
        pairs mapping the phecode id to the phecode name.
        The other map stores all the phecode categories as
        keys and a list of the phecode ids within that
        category as values

    """
    # We need to find the path to each phecode file

    # phecode_filepaths = Path(__file__).parent.parent.parent / "phecode_mappings"

    phecode_map_files = list(phecode_filepaths.glob("*.txt"))

    if len(phecode_map_files) != 2:
        logger.critical(
            f"Unable to detect the files for the PheCode 1.2 & PheCode X mappings. This error probably means they were deleted or the cloning of the github repository partially failed. Attempted search in this directory: {phecode_filepaths}."
        )
        raise FileNotFoundError(
            f"Unable to detect the files for the PheCode 1.2 & PheCode X mappings. This error probably means they were deleted or the cloning of the github repository partially failed.. Attempted search in this directory: {phecode_filepaths}."
        )

    for file in phecode_map_files:
        with open(file, "r") as phecode_file:
            header = next(phecode_file)
            validate_header(header.strip().split("\t"))
            csvreader = csv.reader(phecode_file, delimiter="\t", quotechar='"')
            for line in csvreader:
                phecodeid, desc, category = line
                if "/" in category:
                    category = category.replace("/", "_")
                # There are phecodes in the 1000+ range that have no category.
                # We will use the phrase other here
                if category == "NULL":
                    category = "Other"
                phecode_container.phecode_names[phecodeid] = desc
                phecode_container.category_groups.setdefault(category, []).append(
                    phecodeid
                )
