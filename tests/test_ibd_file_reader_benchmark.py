# This script will allow us to benchmark the functions involved
# in reading in the IBD file and formatting it before beginning
# the cluster algorithm
import pytest
import os
import sys
import polars as pl
from pathlib import Path
from dotenv import load_dotenv

sys.path.append("./src")


from drive.filters import DuckDBFilter, DuckdbTemplate, filter_ibd_file
from drive.helper_funcs import split_target_string
from drive.models import create_indices
from drive.parser import PhenotypeFileParser
from drive.network import generate_edge_info_df, generate_vertex_info_df


##load in the env variables

load_dotenv("tests/.env")

CM_THRESHOLD = os.getenv("CM_THRESHOLD")
FILTER_TYPE = os.getenv("FILTER_TYPE")

TEST_SETS = [
    (
        Path(os.getenv("SMALL_TEST_SET", "")),
        Path(os.getenv("SMALL_SET_PHENO_FILE", "")),
        float(CM_THRESHOLD),  # pyright: ignore[reportArgumentType]
        FILTER_TYPE,
        "20:4666882-4682236",
    ),
    (
        Path(os.getenv("MEDIUM_TEST_SET", "")),
        Path(os.getenv("MEDIUM_SET_PHENO_FILE", "")),
        float(CM_THRESHOLD),  # pyright: ignore[reportArgumentType]
        FILTER_TYPE,
        "21:35818988-35884573",
    ),
    (
        Path(os.getenv("LARGE_TEST_SET", "")),
        Path(os.getenv("LARGE_SET_PHENO_FILE", "")),
        float(CM_THRESHOLD),  # pyright: ignore[reportArgumentType]
        FILTER_TYPE,
        "7:117287120-117715971",
    ),
]

DATASET_IDS = [
    "small_subset_simulated",
    "medium_kcne1_subset",
    "large_agd250k_cftr_subset",
]


def drive_ibd_filtering_steps(
    ibd_file: Path,
    target_gene_str: str,
    min_cm: float,
    cohort_ids: list[str],
    filter_type: str,
) -> None:
    """this function will combine the appropriate steps from drive to simulate how it runs in the code"""
    indices = create_indices("hapibd")

    target_gene = split_target_string(target_gene_str)

    segment_filter = DuckDBFilter(indices, target_gene, filter_type)

    sql_query = DuckdbTemplate(
        ibd_segment_file=ibd_file,
        filterObj=segment_filter,
        indices=indices,
        min_cm=min_cm,
    ).get_network_filter(add_sample_filter=True)

    cohort_id_df = pl.DataFrame({"IDs": cohort_ids})

    filtered_ibd_df = filter_ibd_file(
        sql_query=sql_query, keep_df=cohort_id_df, indices=indices
    )

    edge_info_df, _ = generate_edge_info_df(data=filtered_ibd_df, indices=indices)

    _ = generate_vertex_info_df(data=edge_info_df, indices=indices)


@pytest.mark.parametrize(
    "ibd_file, case_file, min_cm, filter_type, region", TEST_SETS, ids=DATASET_IDS
)
def test_benchmark_load_ibd_file(
    benchmark,
    ibd_file: Path,
    case_file: Path,
    min_cm: float,
    filter_type: str,
    region: str,
) -> None:
    """test the set of functions that reads in the ibd file for future reference"""
    cohort_ids = []
    with PhenotypeFileParser(case_file, None) as phenotype_file:
        _, cohort_ids = phenotype_file.parse_cases_and_controls()

    benchmark(
        drive_ibd_filtering_steps, ibd_file, region, min_cm, cohort_ids, filter_type
    )
