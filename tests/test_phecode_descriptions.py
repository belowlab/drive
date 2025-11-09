import sys
import sysconfig
import pytest
from pathlib import Path

sys.path.append("./src")

from drive.utilities.parser import load_phenotype_descriptions, PhecodesMapper

site_packages_path = Path(sysconfig.get_paths().get("platlib"))


def test_file_not_found() -> None:
    """ensure the FileNotFoundError is being raise if a incorrect filepath is being provided"""
    with pytest.raises(FileNotFoundError):
        load_phenotype_descriptions(
            PhecodesMapper(), []
        )  # empty list represents glob not finding the correct filepath


def test_incorrect_col_name() -> None:
    """check to make sure a ValueError is raised when a file with does not have all of the
    correct column names.  Need to supply 2 files where 1 has the incorrect column names
    """

    pheno_filepath = [
        Path(
            "/data100t1/home/james/bin/drive/drive/tests/test_inputs/test_incorrect_column_phecode_map_file.txt"
        ),
        Path(
            "/data100t1/home/james/bin/drive/drive/tests/test_inputs/test_correct_phecode_map_file.txt"
        ),
    ]

    with pytest.raises(ValueError):
        load_phenotype_descriptions(PhecodesMapper(), pheno_filepath)


def test_incorrect_col_order() -> None:
    """check to make sure a ValueError is raised when the expected columns are not in
    the correct order. Need to suppply 2 files where 1 of them has the columns in the incorrect
    order"""

    pheno_filepath = [
        Path(
            "/data100t1/home/james/bin/drive/drive/tests/test_inputs/test_incorrect_order_phecode_map_file.txt"
        ),
        Path(
            "/data100t1/home/james/bin/drive/drive/tests/test_inputs/test_correct_phecode_map_file.txt"
        ),
    ]

    with pytest.raises(ValueError):
        load_phenotype_descriptions(PhecodesMapper(), pheno_filepath)


# We will use this test data to ensure the description values in the dictionary are being handled correctly
test_output_codes = [
    ("CV_414", "Cardiomyopathy"),
    ("425", "Cardiomyopathy"),
    ("CV_414.1", "Hypertrophic cardiomyopathy"),
]


@pytest.mark.parametrize("phecode,desc", test_output_codes)
def test_output_descriptions(phecode: str, desc: str) -> None:
    """ensure that the appropriate values are being read in to the dictionary"""
    phecode_filepaths = (
        Path(__file__).parent.parent / "src" / "drive" / "phecode_mappings"
    )

    phecode_map_files = list(phecode_filepaths.glob("*.txt"))

    phecodeDescriptions = PhecodesMapper()

    load_phenotype_descriptions(phecodeDescriptions, phecode_map_files)

    # we are going to spot test a few pheotypes and make sure they are in the output dictionary
    #
    assert phecodeDescriptions.phecode_names[phecode] == desc


def test_null_relabel() -> None:
    error_list = []

    # we are going to look for the following phecodes in the output category
    phecodes_to_check = [
        "1000",
        "1001",
        "1002",
        "1003",
        "1004",
        "1005",
        "1006",
        "1007",
        "1008",
        "1009",
        "1010",
        "1011",
        "1012",
        "1013",
        "1014",
        "1015",
        "1019",
    ]

    phecode_filepaths = (
        Path(__file__).parent.parent / "src" / "drive" / "phecode_mappings"
    )

    phecode_map_files = list(phecode_filepaths.glob("*.txt"))

    phecodeDescriptions = PhecodesMapper()

    load_phenotype_descriptions(phecodeDescriptions, phecode_map_files)

    assert (
        phecodeDescriptions.category_groups.get("Other") != None
    ), "no phecodes were mapped to the 'Other' category. Expected 17 phecode 1000+ to be mapped to this category"

    for phecode in phecodes_to_check:

        if phecode not in phecodeDescriptions.category_groups.get("Other"):
            error_list.append(
                f"expected to find the phecode {phecode} in the 'Other' category."
            )

    error_str = "\n".join(error_list)

    assert (
        len(error_list) == 0
    ), f"encountered the following errors while trying to ensure that the 1000+ phecode were mapped to the other category:\n{error_str}"


def test_category_count() -> None:

    number_of_categories_to_expect = 36
    phecode_filepaths = (
        Path(__file__).parent.parent / "src" / "drive" / "phecode_mappings"
    )

    phecode_map_files = list(phecode_filepaths.glob("*.txt"))

    phecodeDescriptions = PhecodesMapper()

    load_phenotype_descriptions(phecodeDescriptions, phecode_map_files)

    categories_read_in = len(phecodeDescriptions.category_groups.keys())

    assert (
        categories_read_in == number_of_categories_to_expect
    ), f"Expected to read in {number_of_categories_to_expect} unique categories, encountered {categories_read_in} unique categories in the file"
