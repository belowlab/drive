from pathlib import Path

import pandas as pd
import pytest

from drive.parser.case_file_parser import (
    load_phenotype_df,
    open_phenotype_file,
    parse_binary_matrix,
    parse_continuous_matrix,
    resolve_phenotype_columns,
)

SAMPLE_CONTENT_BINARY = """GRID\tPhe1\tPhe2
ID1\t1\t0
ID2\t0\t1
ID3\t-1\t1
ID4\tNA\t0
ID5\t1\t-1
"""

SAMPLE_CONTENT_CONTINUOUS = """GRID\tTrait1\tTrait2
ID1\t10.5\t-1.0
ID2\t-2.3\t0.0
ID3\t0.0\t5.5
ID4\tNA\t-1.5
ID5\t-1.0\tNA
"""


@pytest.fixture
def valid_binary_file(tmp_path: Path) -> Path:
    """Create a temporary tab-separated binary phenotype file."""
    p = tmp_path / "binary_phenotypes.txt"
    p.write_text(SAMPLE_CONTENT_BINARY, encoding="utf-8")
    return p


@pytest.fixture
def valid_continuous_file(tmp_path: Path) -> Path:
    """Create a temporary tab-separated continuous phenotype file."""
    p = tmp_path / "continuous_phenotypes.txt"
    p.write_text(SAMPLE_CONTENT_CONTINUOUS, encoding="utf-8")
    return p


@pytest.mark.unit
def test_load_phenotype_df_not_found() -> None:
    """Test that FileNotFoundError is raised when file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_phenotype_df("non_existent_file.txt")


@pytest.mark.unit
def test_load_phenotype_df_binary(valid_binary_file: Path) -> None:
    """Test loading binary phenotype data where missing and -1 are filled with -1."""
    df = load_phenotype_df(valid_binary_file, is_continuous=False)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (5, 3)

    # In binary mode, NA should be filled with -1
    row_id4 = df.loc[df.iloc[:, 0] == "ID4"]
    assert row_id4["Phe1"].values[0] == -1


@pytest.mark.unit
def test_load_phenotype_df_continuous(valid_continuous_file: Path) -> None:
    """Test loading continuous data where -1.0 is preserved and true NAs are NaN."""
    df = load_phenotype_df(valid_continuous_file, is_continuous=True)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (5, 3)

    # -1.0 must be preserved as valid numeric data, NOT coerced to missing or -1 fillna
    row_id5 = df.loc[df.iloc[:, 0] == "ID5"]
    assert row_id5["Trait1"].values[0] == -1.0

    # True NA should remain NaN
    row_id4 = df.loc[df.iloc[:, 0] == "ID4"]
    assert pd.isna(row_id4["Trait1"].values[0])


@pytest.mark.unit
def test_resolve_columns_all(valid_binary_file: Path) -> None:
    """Test resolving all phenotype columns when none is specified."""
    df = load_phenotype_df(valid_binary_file)
    cols = resolve_phenotype_columns(df)
    assert cols == ["Phe1", "Phe2"]


@pytest.mark.unit
def test_resolve_columns_specific(valid_binary_file: Path) -> None:
    """Test resolving a specific phenotype column."""
    df = load_phenotype_df(valid_binary_file)
    cols = resolve_phenotype_columns(df, phenotype_name="Phe1")
    assert cols == ["Phe1"]


@pytest.mark.unit
def test_resolve_columns_not_found(valid_binary_file: Path) -> None:
    """Test error when specified phenotype is missing."""
    df = load_phenotype_df(valid_binary_file)
    with pytest.raises(ValueError, match="not found"):
        resolve_phenotype_columns(df, phenotype_name="PheMissing")


@pytest.mark.unit
def test_parse_binary_matrix(valid_binary_file: Path) -> None:
    """Test classification into cases, controls, and exclusions for binary traits."""
    df = load_phenotype_df(valid_binary_file, is_continuous=False)
    cols = resolve_phenotype_columns(df)
    pheno_dict, cohort = parse_binary_matrix(df, cols)

    assert len(cohort) == 5

    # Phe1: cases=[ID1, ID5], controls=[ID2], excluded=[ID3, ID4]
    phe1 = pheno_dict["Phe1"]
    assert phe1["cases"] == {"ID1", "ID5"}
    assert phe1["controls"] == {"ID2"}
    assert phe1["excluded"] == {"ID3", "ID4"}

    # Phe2: cases=[ID2, ID3], controls=[ID1, ID4], excluded=[ID5]
    phe2 = pheno_dict["Phe2"]
    assert phe2["cases"] == {"ID2", "ID3"}
    assert phe2["controls"] == {"ID1", "ID4"}
    assert phe2["excluded"] == {"ID5"}


@pytest.mark.unit
def test_parse_continuous_matrix(valid_continuous_file: Path) -> None:
    """Test extraction of continuous numeric values and missing exclusions."""
    df = load_phenotype_df(valid_continuous_file, is_continuous=True)
    cols = resolve_phenotype_columns(df)
    pheno_dict, cohort = parse_continuous_matrix(df, cols)

    assert len(cohort) == 5

    # Trait1: ID1=10.5, ID2=-2.3, ID3=0.0, ID4=NA (excluded), ID5=-1.0
    trait1 = pheno_dict["Trait1"]
    assert trait1["values"]["ID1"] == 10.5
    assert trait1["values"]["ID2"] == -2.3
    assert trait1["values"]["ID3"] == 0.0
    assert trait1["values"]["ID5"] == -1.0
    assert "ID4" not in trait1["values"]
    assert trait1["excluded"] == {"ID4"}

    # Trait2: ID1=-1.0, ID2=0.0, ID3=5.5, ID4=-1.5, ID5=NA (excluded)
    trait2 = pheno_dict["Trait2"]
    assert trait2["values"]["ID1"] == -1.0
    assert trait2["values"]["ID2"] == 0.0
    assert trait2["values"]["ID3"] == 5.5
    assert trait2["values"]["ID4"] == -1.5
    assert "ID5" not in trait2["values"]
    assert trait2["excluded"] == {"ID5"}


@pytest.mark.unit
def test_open_phenotype_file_binary(valid_binary_file: Path) -> None:
    """Test the open_phenotype_file context manager in binary mode."""
    with open_phenotype_file(valid_binary_file, is_continuous=False) as (
        pheno_dict,
        cohort,
    ):
        assert "Phe1" in pheno_dict
        assert "Phe2" in pheno_dict
        assert len(cohort) == 5
        assert pheno_dict["Phe1"]["cases"] == {"ID1", "ID5"}


@pytest.mark.unit
def test_open_phenotype_file_continuous(valid_continuous_file: Path) -> None:
    """Test the open_phenotype_file context manager in continuous mode."""
    with open_phenotype_file(
        valid_continuous_file, phenotype_name="Trait1", is_continuous=True
    ) as (pheno_dict, cohort):
        assert list(pheno_dict.keys()) == ["Trait1"]
        assert len(cohort) == 5
        assert pheno_dict["Trait1"]["values"]["ID5"] == -1.0
        assert pheno_dict["Trait1"]["excluded"] == {"ID4"}
