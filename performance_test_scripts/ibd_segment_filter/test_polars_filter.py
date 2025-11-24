import pytest

from pathlib import Path
from dotenv import load_dotenv
import os


from .polars_filter import filter_ibd_segments_new
from drive.helper_funcs import split_target_string

load_dotenv(Path(__file__).parent / ".env")

TEST_CASES = [
    (
        Path(os.getenv("SMALL_TEST_SET")),
        Path(os.getenv("SMALL_TEST_DRIVE_RESULTS")),
        "overlaps",
        "20:4666882-4682236",
    ),
    (
        Path(os.getenv("MEDIUM_TEST_SET")),
        Path(os.getenv("MEDIUM_TEST_DRIVE_RESULTS")),
        "overlaps",
        "21:35818988-35884573",
    ),
    (
        Path(os.getenv("LARGE_TEST_SET")),
        Path(os.getenv("LARGE_TEST_DRIVE_RESULTS")),
        "overlaps",
        "7:117287120-117715971",
    ),
]

DATASET_IDS = [
    "small_subset_simulated",
    "medium_kcne1_subset",
    "large_agd250k_cftr_subset",
]


@pytest.mark.parametrize(
    "ibd_file, drive_results, filter_type, region", TEST_CASES, ids=DATASET_IDS
)
@pytest.mark.limit_memory("95 GB")
def test_polars_filter_performance(
    benchmark,
    request,
    ibd_file: Path,
    drive_results: Path,
    filter_type: str,
    region: str,
) -> None:
    """check the polars filter function using different size inputs"""

    current_id = request.node.callspec.id

    benchmark.extra_info["dataset_id"] = current_id

    gene_target = split_target_string(region)

    benchmark(
        filter_ibd_segments_new, ibd_file, drive_results, filter_type, gene_target
    )
