from argparse import Namespace
import gzip
from pathlib import Path

import pytest

from drive.utilities.functions import pull_network_enrichment
from drive.utilities.functions.pull_network_enrichment import (
    gather_pvalues,
    parse_header,
    read_network_ids,
)


@pytest.fixture
def mock_networks_file(tmp_path: Path) -> Path:
    """Fixture providing a text file with network IDs."""
    file_path = tmp_path / "target_networks.txt"
    file_path.write_text("0\n1\n3\n", encoding="utf-8")
    return file_path


@pytest.fixture
def mock_results_header() -> str:
    """Fixture providing a sample DRIVE results header line."""
    return (
        "clstID\tn.total\tn.haplotype\ttrue.positive.n\ttrue.positive\tfalse.positive\tIDs\tID.haplotype\t"
        "min_pvalue\tmin_phenotype\tmin_phenotype_description\t"
        "CV_414_case_count_in_network\tCV_414_cases_in_network\tCV_414_excluded_count_in_network\tCV_414_excluded_in_network\tCV_414_pvalue\t"
        "NS_324.11_case_count_in_network\tNS_324.11_cases_in_network\tNS_324.11_excluded_count_in_network\tNS_324.11_excluded_in_network\tNS_324.11_pvalue\t"
        "phenoC_case_count_in_network\tphenoC_cases_in_network\tphenoC_excluded_count_in_network\tphenoC_excluded_in_network\tphenoC_pvalue\n"
    )


@pytest.fixture
def mock_results_file(tmp_path: Path, mock_results_header: str) -> Path:
    """Fixture providing a sample DRIVE results file."""
    file_path = tmp_path / "results.drive_networks.txt"
    rows = [
        mock_results_header,
        "0\t4\t4\t4\t0.6667\t0\t842,130\t130.1\t0.01\tCV_414\tdesc\t1\t842\t0\tNone\t0.01\t0\tN/A\t0\tNone\t0.5\t0\tN/A\t0\tNone\t1.0\n",
        "1\t2\t2\t1\t1.0000\t0\t223,443\t223.1\t0.05\tNS_324.11\tdesc\t0\tN/A\t0\tNone\t0.8\t1\t223\t0\tNone\t0.05\t0\tN/A\t0\tNone\t0.9\n",
        "2\t2\t2\t1\t1.0000\t0\t253,957\t253.2\t1.0\tN/A\tdesc\t0\tN/A\t0\tNone\t1.0\t0\tN/A\t0\tNone\t1.0\t0\tN/A\t0\tNone\t1.0\n",
        "3\t3\t3\t3\t1.0000\t0\t244,531\t244.1\t0.001\tphenoC\tdesc\t0\tN/A\t0\tNone\t0.3\t0\tN/A\t0\tNone\t0.4\t2\t244,531\t0\tNone\t0.001\n",
    ]
    file_path.write_text("".join(rows), encoding="utf-8")
    return file_path


@pytest.mark.unit
def test_read_network_ids(mock_networks_file: Path) -> None:
    """Test reading network IDs from a text file into a set."""
    network_ids = read_network_ids(mock_networks_file)
    assert isinstance(network_ids, set)
    assert network_ids == {"0", "1", "3"}


@pytest.mark.unit
def test_parse_header(mock_results_header: str) -> None:
    """Test parsing the header to extract phecode p-value column indices."""
    indices = parse_header(mock_results_header)
    assert indices == [
        ("CV_414", 15),
        ("NS_324.11", 20),
        ("phenoC", 25),
    ]
    # Ensure min_pvalue is not included
    assert "min_pvalue" not in [name for name, _ in indices]


@pytest.mark.unit
def test_parse_header_no_phenotypes() -> None:
    """Test parse_header when results file has no phenotype columns."""
    header = "clstID\tn.total\tn.haplotype\ttrue.positive.n\ttrue.positive\tfalse.positive\tIDs\tID.haplotype\n"
    indices = parse_header(header)
    assert indices == []


@pytest.mark.unit
def test_gather_pvalues(mock_results_header: str) -> None:
    """Test extracting pvalues for a single network row."""
    indices = parse_header(mock_results_header)
    row = (
        "0\t4\t4\t4\t0.6667\t0\t842,130\t130.1\t0.01\tCV_414\tdesc\t"
        "1\t842\t0\tNone\t0.01\t0\tN/A\t0\tNone\t0.5\t0\tN/A\t0\tNone\t1.0"
    ).split("\t")
    pvalues = gather_pvalues(row, indices)
    assert pvalues == {
        "CV_414": "0.01",
        "NS_324.11": "0.5",
        "phenoC": "1.0",
    }


@pytest.mark.unit
def test_pull_network_enrichment_single_network(
    mock_results_file: Path, tmp_path: Path
) -> None:
    """Test pulling enrichment results for a single network ID."""
    output_file = tmp_path / "output_single.txt"
    args = Namespace(
        network_id="0",
        networks_file=None,
        results_file=mock_results_file,
        output=output_file,
    )
    pull_network_enrichment(args)

    assert output_file.exists()
    lines = output_file.read_text(encoding="utf-8").strip().split("\n")
    assert lines[0] == "network_id\tphecode_id\tphecode_pvalue"
    assert lines[1] == "0\tCV_414\t0.01"
    assert lines[2] == "0\tNS_324.11\t0.5"
    assert lines[3] == "0\tphenoC\t1.0"
    assert len(lines) == 4


@pytest.mark.unit
def test_pull_network_enrichment_from_file(
    mock_results_file: Path, mock_networks_file: Path, tmp_path: Path
) -> None:
    """Test pulling enrichment results for multiple networks from a text file."""
    output_file = tmp_path / "output_multiple.txt"
    args = Namespace(
        network_id=None,
        networks_file=mock_networks_file,
        results_file=mock_results_file,
        output=output_file,
    )
    pull_network_enrichment(args)

    assert output_file.exists()
    lines = output_file.read_text(encoding="utf-8").strip().split("\n")
    assert lines[0] == "network_id\tphecode_id\tphecode_pvalue"
    # Networks 0, 1, 3 should each have 3 phecodes -> 1 header + 9 rows = 10 lines
    assert len(lines) == 10

    # Ensure network 2 is not present in output
    network_ids_in_output = {line.split("\t")[0] for line in lines[1:]}
    assert network_ids_in_output == {"0", "1", "3"}


@pytest.mark.unit
def test_pull_network_enrichment_gzip_results(
    mock_results_file: Path, tmp_path: Path
) -> None:
    """Test pulling enrichment results from a gzip-compressed results file."""
    gz_results = tmp_path / "results.drive_networks.txt.gz"
    with open(mock_results_file, "rb") as f_in, gzip.open(gz_results, "wb") as f_out:
        f_out.writelines(f_in)

    output_file = tmp_path / "output_from_gz.txt"
    args = Namespace(
        network_id="1",
        networks_file=None,
        results_file=gz_results,
        output=output_file,
    )
    pull_network_enrichment(args)

    assert output_file.exists()
    lines = output_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 4
    assert lines[1] == "1\tCV_414\t0.8"
    assert lines[2] == "1\tNS_324.11\t0.05"
    assert lines[3] == "1\tphenoC\t0.9"


@pytest.mark.unit
def test_pull_network_enrichment_gzip_output(
    mock_results_file: Path, tmp_path: Path
) -> None:
    """Test writing enrichment results to a gzip-compressed output file."""
    gz_output = tmp_path / "output.txt.gz"
    args = Namespace(
        network_id="0",
        networks_file=None,
        results_file=mock_results_file,
        output=gz_output,
    )
    pull_network_enrichment(args)

    assert gz_output.exists()
    with gzip.open(gz_output, "rt", encoding="utf-8") as f_in:
        lines = f_in.read().strip().split("\n")
    assert lines[0] == "network_id\tphecode_id\tphecode_pvalue"
    assert len(lines) == 4
