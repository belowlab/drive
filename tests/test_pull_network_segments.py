from argparse import Namespace
import gzip
from pathlib import Path

import pytest

from drive.utilities.pull_segments import (
    get_header_columns,
    load_network_members,
    pull_network_segments,
    read_network_ids,
)


@pytest.fixture
def mock_networks_file(tmp_path: Path) -> Path:
    """Fixture providing a text file with network IDs."""
    file_path = tmp_path / "target_networks.txt"
    file_path.write_text("0\n3\n999\n", encoding="utf-8")
    return file_path


@pytest.fixture
def mock_drive_file(tmp_path: Path) -> Path:
    """Fixture providing a mock DRIVE results file."""
    file_path = tmp_path / "test_results.drive_networks.txt"
    rows = [
        "clstID\tn.total\tn.haplotype\ttrue.positive.n\ttrue.positive\tfalst.postive\tIDs\tID.haplotype\n",
        "0\t4\t4\t4\t0.6667\t0\t30,130,861,842\t130.1,842.1,30.2,861.2\n",
        "3\t3\t3\t3\t1.0000\t0\t531,244,231\t231.1,244.1,531.2\n",
        "4\t5\t5\t7\t0.7000\t0\t574,676,210,535,94\t535.1,574.2,94.1,210.1,676.2\n",
    ]
    file_path.write_text("".join(rows), encoding="utf-8")
    return file_path


@pytest.fixture
def mock_drive_file_gz(tmp_path: Path, mock_drive_file: Path) -> Path:
    """Fixture providing a gzipped mock DRIVE results file."""
    gz_path = tmp_path / "test_results.drive_networks.txt.gz"
    with open(mock_drive_file, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        f_out.writelines(f_in)
    return gz_path


@pytest.mark.unit
def test_read_network_ids(mock_networks_file: Path) -> None:
    """Test reading network IDs from a file into a set."""
    ids = read_network_ids(mock_networks_file)
    assert isinstance(ids, set)
    assert ids == {"0", "3", "999"}


@pytest.mark.unit
def test_read_network_ids_tab_separated(tmp_path: Path) -> None:
    """Test reading network IDs from a tab-separated file."""
    tsv_file = tmp_path / "target_networks.tsv"
    tsv_file.write_text("0\tsome_annotation\n3\tother\n", encoding="utf-8")
    ids = read_network_ids(tsv_file)
    assert ids == {"0", "3"}


@pytest.mark.unit
def test_load_network_members_plaintext(mock_drive_file: Path) -> None:
    """Test extracting member IDs and haplotypes from a plaintext DRIVE results file."""
    found, missing = load_network_members(mock_drive_file, {"0", "3", "999"})
    assert "0" in found
    assert "3" in found
    assert "999" not in found
    assert missing == {"999"}

    assert found["0"]["samples"] == {"30", "130", "861", "842"}
    assert found["0"]["haplotypes"] == {"130.1", "842.1", "30.2", "861.2"}

    assert found["3"]["samples"] == {"531", "244", "231"}
    assert found["3"]["haplotypes"] == {"231.1", "244.1", "531.2"}


@pytest.mark.unit
def test_load_network_members_gzipped(mock_drive_file_gz: Path) -> None:
    """Test extracting member IDs and haplotypes from a gzipped DRIVE results file."""
    found, missing = load_network_members(mock_drive_file_gz, {"0"})
    assert "0" in found
    assert missing == set()
    assert found["0"]["samples"] == {"30", "130", "861", "842"}


@pytest.mark.unit
def test_get_header_columns() -> None:
    """Test header generation for all supported IBD formats and fallback."""
    # hapibd: 8 raw columns
    assert get_header_columns("hapibd", 8) == [
        "clstID",
        "id1",
        "hap1",
        "id2",
        "hap2",
        "chr",
        "start",
        "end",
        "cM",
    ]

    # rapid: 8 raw columns (different column order)
    assert get_header_columns("rapid", 8) == [
        "clstID",
        "chr",
        "id1",
        "id2",
        "hap1",
        "hap2",
        "start",
        "end",
        "cM",
    ]

    # germline: 11 raw columns
    assert get_header_columns("germline", 11) == [
        "clstID",
        "id1",
        "hap1",
        "id2",
        "hap2",
        "chr",
        "start",
        "end",
        "snp_start",
        "snp_end",
        "total_snps",
        "cM",
    ]

    # ilash: 9 raw columns
    assert get_header_columns("ilash", 9) == [
        "clstID",
        "id1",
        "hap1",
        "id2",
        "hap2",
        "chr",
        "start",
        "end",
        "snp_count",
        "cM",
    ]

    # fallback for unknown format
    assert get_header_columns("custom", 3) == [
        "clstID",
        "column0",
        "column1",
        "column2",
    ]


@pytest.mark.unit
def test_pull_network_segments_none_found(
    mock_drive_file: Path, tmp_path: Path
) -> None:
    """Test that pull_network_segments exits with code 1 when no networks are found."""
    out_file = tmp_path / "output.ibd"
    args = Namespace(
        network_id="nonexistent_id",
        networks_file=None,
        drive_file=mock_drive_file,
        ibd_file=Path("nonexistent.ibd"),
        target="20:100-200",
        format="hapibd",
        min_cm=3,
        segment_overlap="contains",
        threads=1,
        max_memory=None,
        temp_dir=None,
        output=out_file,
    )

    with pytest.raises(SystemExit) as exc_info:
        pull_network_segments(args)
    assert exc_info.value.code == 1


@pytest.mark.integtest
def test_pull_network_segments_end_to_end(tmp_path: Path) -> None:
    """Test pulling pairwise segments end-to-end on simulated dataset."""
    drive_file = Path(
        "tests/test_inputs/integration_dendrogram_test_results_no_pheno.drive_networks.txt"
    )
    ibd_file = Path("tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz")
    out_file = tmp_path / "pulled_segments.ibd"

    args = Namespace(
        network_id="0",
        networks_file=None,
        drive_file=drive_file,
        ibd_file=ibd_file,
        target="20:4666882-4682236",
        format="hapibd",
        min_cm=3,
        segment_overlap="contains",
        threads=2,
        max_memory=None,
        temp_dir=None,
        output=out_file,
    )

    pull_network_segments(args)

    assert out_file.exists()
    lines = out_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) > 1  # Header + at least one segment

    header = lines[0].split("\t")
    assert header[0] == "clstID"
    assert header[1:] == ["id1", "hap1", "id2", "hap2", "chr", "start", "end", "cM"]

    # Verify all output rows have clstID == 0
    for row in lines[1:]:
        split_row = row.split("\t")
        assert split_row[0] == "0"
        # Network 0 haplotypes are 130.1, 842.1, 30.2, 861.2
        hap1 = f"{split_row[1]}.{split_row[2]}"
        hap2 = f"{split_row[3]}.{split_row[4]}"
        assert hap1 in {"130.1", "842.1", "30.2", "861.2"}
        assert hap2 in {"130.1", "842.1", "30.2", "861.2"}


@pytest.mark.integtest
def test_pull_network_segments_gz_output(tmp_path: Path) -> None:
    """Test that pull_network_segments correctly creates a gzipped output file."""
    drive_file = Path(
        "tests/test_inputs/integration_dendrogram_test_results_no_pheno.drive_networks.txt"
    )
    ibd_file = Path("tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz")
    out_file = tmp_path / "pulled_segments.ibd.gz"

    args = Namespace(
        network_id="0",
        networks_file=None,
        drive_file=drive_file,
        ibd_file=ibd_file,
        target="20:4666882-4682236",
        format="hapibd",
        min_cm=3,
        segment_overlap="contains",
        threads=2,
        max_memory=None,
        temp_dir=None,
        output=out_file,
    )

    pull_network_segments(args)

    assert out_file.exists()
    with gzip.open(out_file, "rt", encoding="utf-8") as gz_in:
        content = gz_in.read()
    lines = content.strip().split("\n")
    assert len(lines) > 1
    assert lines[0].startswith("clstID\t")
