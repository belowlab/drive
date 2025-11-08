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
        load_phenotype_descriptions(PhecodesMapper(), Path("test_fake_filepath"))
