import pytest
import pandas as pd
from pathlib import Path
from drive.parser.case_file_parser import PhenotypeFileParser

# Define some sample data for creating temporary files
SAMPLE_CONTENT_TAB = """GRID	Phe1	Phe2
ID1	1	0
ID2	0	1
ID3	-1	1
ID4	NA	0
ID5	1	-1
"""

SAMPLE_CONTENT_BAD = """GRID,Phe1,Phe2
ID1,1,0
ID2,0,1
"""


@pytest.fixture
def valid_phenotype_file(tmp_path):
    """Creates a valid tab-separated phenotype file."""
    p = tmp_path / "phenotypes.txt"
    p.write_text(SAMPLE_CONTENT_TAB, encoding="utf-8")
    return p


@pytest.fixture
def invalid_format_file(tmp_path):
    """Creates a file with comma separators (invalid for this parser)."""
    p = tmp_path / "phenotypes_bad.csv"
    p.write_text(SAMPLE_CONTENT_BAD, encoding="utf-8")
    return p


@pytest.mark.unit
def test_init_file_not_found():
    """Test that FileNotFoundError is raised when file does not exist."""
    with pytest.raises(FileNotFoundError):
        PhenotypeFileParser("non_existent_file.txt")


@pytest.mark.unit
def test_correct_attributes(valid_phenotype_file):
    """Test that the context manager loads the DataFrame correctly."""
    with PhenotypeFileParser(valid_phenotype_file) as parser:
        assert hasattr(parser, "phenotype_df")
        assert isinstance(parser.phenotype_df, pd.DataFrame)
        # 5 individuals, 3 columns (GRID, Phe1, Phe2)
        assert parser.phenotype_df.shape == (5, 3)
        # Check NA handling: 'na' should be -1.0 (or -1 depending on dtype)
        # pandas read_csv with na_values will make it NaN, then fillna(-1) makes it -1.0 usually for floats
        # ID4 Phe1 was 'na'
        row_id4 = parser.phenotype_df.loc[parser.phenotype_df.iloc[:, 0] == "ID4"]
        assert row_id4["Phe1"].values[0] == -1


@pytest.mark.unit
def test_columns_to_keep_all(valid_phenotype_file):
    """Test retrieving all phenotype columns."""
    with PhenotypeFileParser(valid_phenotype_file) as parser:
        cols = parser._generate_columns_to_keep()
        assert set(cols) == {"Phe1", "Phe2"}


@pytest.mark.unit
def test_columns_to_keep_specific(valid_phenotype_file):
    """Test retrieving a specific phenotype column."""
    with PhenotypeFileParser(valid_phenotype_file, phenotype_name="Phe1") as parser:
        cols = parser._generate_columns_to_keep()
        assert cols == ["Phe1"]


@pytest.mark.unit
def test_columns_to_keep_specific_not_found(valid_phenotype_file):
    """Test error when specific phenotype is missing."""
    with PhenotypeFileParser(
        valid_phenotype_file, phenotype_name="PheMissing"
    ) as parser:
        with pytest.raises(ValueError, match="not found"):
            parser._generate_columns_to_keep()


@pytest.mark.unit
def test_parse_cases_and_controls_logic(valid_phenotype_file):
    """Test the logic for classifying cases, controls, and exclusions."""
    # Data Recap:
    # GRID	Phe1	Phe2
    # ID1	1	0
    # ID2	0	1
    # ID3	-1	1
    # ID4	na	0
    # ID5	1	-1

    # Phe1:
    # Cases (1): ID1, ID5
    # Controls (0): ID2
    # Excluded (-1, na): ID3, ID4

    with PhenotypeFileParser(valid_phenotype_file) as parser:
        pheno_dict, cohort = parser.parse_cases_and_controls()

        phe1 = pheno_dict["Phe1"]
        assert "ID1" in phe1["cases"]
        assert "ID5" in phe1["cases"]
        assert "ID2" in phe1["controls"]
        assert "ID3" in phe1["excluded"]
        assert "ID4" in phe1["excluded"]  # na -> -1

        assert len(phe1["cases"]) == 2
        assert len(phe1["controls"]) == 1
        assert len(phe1["excluded"]) == 2

        # Phe2:
        # Cases: ID2, ID3
        # Controls: ID1, ID4
        # Excluded: ID5
        phe2 = pheno_dict["Phe2"]
        assert "ID2" in phe2["cases"]
        assert "ID3" in phe2["cases"]
        assert "ID1" in phe2["controls"]
        assert "ID4" in phe2["controls"]
        assert "ID5" in phe2["excluded"]

        assert len(cohort) == 5
