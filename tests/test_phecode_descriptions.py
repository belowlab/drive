import sys
import sysconfig
import pytest
import os
from pathlib import Path

sys.path.append("./src")

from drive import drive
from drive.utilities.parser import load_phenotype_descriptions, PhecodesMapper

site_packages_path = Path(sysconfig.get_paths().get("platlib"))


def test_file_not_found() -> None:
    """ensure the FileNotFoundError is being raise if a incorrect filepath is being provided"""
    with pytest.raises(FileNotFoundError):
        load_phenotype_descriptions(
            PhecodesMapper(), []
        )  # empty list represents glob not finding the correct filepath


def test_incorrect_col_name() -> None:
    """check to make sure a ValueError is raised when a file with does not have all of the correct column names"""

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
    """check to make sure a ValueError is raised when the expected columns are not in the correct order"""

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
