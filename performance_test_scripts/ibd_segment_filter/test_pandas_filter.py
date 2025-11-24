import pytest

from pathlib import Path
from dotenv import load_dotenv
import os


from .pandas_filter import pandas_ibd_filter
from drive.helper_funcs import split_target_string

load_dotenv(Path(__file__).parent / ".env")

TEST_CASES = [
    (
        Path(os.getenv("SMALL_TEST_SET")),
        "hapibd",
        "overlaps",
        "20:4666882-4682236",
        3.0,
        10_000_000,
    ),
    (
        Path(os.getenv("MEDIUM_TEST_SET")),
        "hapibd",
        "overlaps",
        "21:35818988-35884573",
        3.0,
        10_000_000,
    ),
    (
        Path(os.getenv("LARGE_TEST_SET")),
        "hapibd",
        "overlaps",
        "7:117287120-117715971",
        3.0,
        10_000_000,
    ),
]

DATASET_IDS = [
    "small_subset_simulated_pandas",
    "medium_kcne1_subset_pandas",
    "large_agd250k_cftr_subset_pandas",
]


@pytest.mark.parametrize(
    "ibd_file, ibd_format, filter_type, region, min_cm, chunksize",
    TEST_CASES,
    ids=DATASET_IDS,
)
def test_pandas_filter_performance(
    benchmark,
    request,
    ibd_file: Path,
    ibd_format: str,
    filter_type: str,
    region: str,
    min_cm: float,
    chunksize: int,
) -> None:
    """check the polars filter function using different size inputs"""

    current_id = request.node.callspec.id

    benchmark.extra_info["dataset_id"] = current_id

    benchmark(
        pandas_ibd_filter, ibd_file, ibd_format, filter_type, region, min_cm, chunksize
    )
