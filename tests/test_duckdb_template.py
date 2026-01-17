import pytest
from pathlib import Path
import sys
import sysconfig
import re

sys.path.append("./src")

from drive.models import create_indices
from drive.helper_funcs import split_target_string
from drive.filters import DuckdbTemplate, DuckDBFilter

site_packages_path = Path(sysconfig.get_paths().get("platlib"))


@pytest.fixture
def make_query_statement() -> Path:
    return (
        site_packages_path / "tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz"
    )


def normalize_sql(sql: str) -> str:
    """sanitize the SQL statement by removing newlines and collapsing whitespace into 1 row

    Parameters
    ----------
    sql : str
        original SQL query string

    Returns
    -------
    str
        returns the sanitized string
    """

    return re.sub(r"\s+", " ", sql).strip()


def test_SQL_statment_sample_query_and_overlaps(make_query_statement) -> None:
    """Test the SQL statement that is provided by the DuckdbTemplate when you
    choose to filter for samples and use the 'overlaps' option for
    --segment-overlap flag

    Parameter
    ---------
    make_query_statement
        pytest fixture that adds the path to the test ibd file
    """
    ## Lets create the actual string that we want
    expected_SQL = f"""
        SELECT
            t.*
        FROM read_csv(
            '{make_query_statement}',
            delim='\t',
            header=False,
            columns={{
                'column0':'VARCHAR',
                'column1':'VARCHAR',
                'column2':'VARCHAR',
                'column3':'VARCHAR',
                'column4':'VARCHAR',
                'column5':'BIGINT',
                'column6':'BIGINT',
                'column7':'DOUBLE'

            }}
        ) as t
        WHERE
            t.column0 IN (SELECT IDs FROM ids_df) AND t.column2 IN (SELECT IDs FROM ids_df) AND 
            (
                (t.column5 <= 4666882 AND t.column6 >= 4666882) OR
                (t.column5 >= 4666882 AND t.column6 <= 4682236) OR
                (t.column5 <= 4682236 AND t.column6 >= 4682236)
            )
            AND t.column7 >= 3.0
        """

    indices = create_indices("hapibd")

    region = split_target_string("20:4666882-4682236")

    filter_type = DuckDBFilter(indices, region, "overlaps")

    sql_query = DuckdbTemplate(
        ibd_segment_file=make_query_statement,
        filterObj=filter_type,
        indices=indices,
        min_cm=3.0,
    ).get_network_filter(add_sample_filter=True)
    # We are going to sanitize the strings just because there can be issues with whitespace that we don't want to break the test
    normalized_generated_query = normalize_sql(sql_query.strip())
    normalized_expected_query = normalize_sql(expected_SQL.strip())

    assert (
        normalized_generated_query == normalized_expected_query
    ), f"Expected the query string to be\n{normalized_expected_query}\nInstead found the query\n{normalized_generated_query}\n"


def test_SQL_statment_sample_query_and_contains(make_query_statement) -> None:
    """Test the SQL statement that is provided by the DuckdbTemplate when you
    choose to filter for samples and use the 'contains' option for
    --segment-overlap flag

    Parameter
    ---------
    make_query_statement
        pytest fixture that adds the path to the test ibd file
    """
    ## Lets create the actual string that we want
    expected_SQL = f"""
        SELECT
            t.*
        FROM read_csv(
            '{make_query_statement}',
            delim='\t',
            header=False,
            columns={{
                'column0':'VARCHAR',
                'column1':'VARCHAR',
                'column2':'VARCHAR',
                'column3':'VARCHAR',
                'column4':'VARCHAR',
                'column5':'BIGINT',
                'column6':'BIGINT',
                'column7':'DOUBLE'

            }}
        ) as t
        WHERE
            t.column0 IN (SELECT IDs FROM ids_df) AND t.column2 IN (SELECT IDs FROM ids_df) AND 
            (t.column5 <= 4666882 AND t.column6 >= 4682236)
            AND t.column7 >= 3.0
        """

    indices = create_indices("hapibd")

    region = split_target_string("20:4666882-4682236")

    filter_type = DuckDBFilter(indices, region, "contains")

    sql_query = DuckdbTemplate(
        ibd_segment_file=make_query_statement,
        filterObj=filter_type,
        indices=indices,
        min_cm=3.0,
    ).get_network_filter(add_sample_filter=True)
    # We are going to sanitize the strings just because there can be issues with whitespace that we don't want to break the test
    normalized_generated_query = normalize_sql(sql_query.strip())
    normalized_expected_query = normalize_sql(expected_SQL.strip())

    assert (
        normalized_generated_query == normalized_expected_query
    ), f"Expected the query string to be\n{normalized_expected_query}\nInstead found the query\n{normalized_generated_query}\n"


def test_SQL_statment_no_sample_query_and_overlaps(make_query_statement) -> None:
    """Test the SQL statement that is provided by the DuckdbTemplate when you
    choose to filter for samples and use the 'contains' option for
    --segment-overlap flag

    Parameter
    ---------
    make_query_statement
        pytest fixture that adds the path to the test ibd file
    """
    ## Lets create the actual string that we want
    expected_SQL = f"""
        SELECT
            t.*
        FROM read_csv(
            '{make_query_statement}',
            delim='\t',
            header=False,
            columns={{
                'column0':'VARCHAR',
                'column1':'VARCHAR',
                'column2':'VARCHAR',
                'column3':'VARCHAR',
                'column4':'VARCHAR',
                'column5':'BIGINT',
                'column6':'BIGINT',
                'column7':'DOUBLE'

            }}
        ) as t
        WHERE
            (
                (t.column5 <= 4666882 AND t.column6 >= 4666882) OR
                (t.column5 >= 4666882 AND t.column6 <= 4682236) OR
                (t.column5 <= 4682236 AND t.column6 >= 4682236)
            )
            AND t.column7 >= 3.0
        """

    indices = create_indices("hapibd")

    region = split_target_string("20:4666882-4682236")

    filter_type = DuckDBFilter(indices, region, "overlaps")

    sql_query = DuckdbTemplate(
        ibd_segment_file=make_query_statement,
        filterObj=filter_type,
        indices=indices,
        min_cm=3.0,
    ).get_network_filter(add_sample_filter=False)
    # We are going to sanitize the strings just because there can be issues with whitespace that we don't want to break the test
    normalized_generated_query = normalize_sql(sql_query.strip())
    normalized_expected_query = normalize_sql(expected_SQL.strip())

    assert (
        normalized_generated_query == normalized_expected_query
    ), f"Expected the query string to be\n{normalized_expected_query}\nInstead found the query\n{normalized_generated_query}\n"


def test_SQL_statment_no_sample_query_and_contains(make_query_statement) -> None:
    """Test the SQL statement that is provided by the DuckdbTemplate when you
    choose to filter for samples and use the 'contains' option for
    --segment-overlap flag

    Parameter
    ---------
    make_query_statement
        pytest fixture that adds the path to the test ibd file
    """
    ## Lets create the actual string that we want
    expected_SQL = f"""
        SELECT
            t.*
        FROM read_csv(
            '{make_query_statement}',
            delim='\t',
            header=False,
            columns={{
                'column0':'VARCHAR',
                'column1':'VARCHAR',
                'column2':'VARCHAR',
                'column3':'VARCHAR',
                'column4':'VARCHAR',
                'column5':'BIGINT',
                'column6':'BIGINT',
                'column7':'DOUBLE'

            }}
        ) as t
        WHERE
            (t.column5 <= 4666882 AND t.column6 >= 4682236)
            AND t.column7 >= 3.0
        """

    indices = create_indices("hapibd")

    region = split_target_string("20:4666882-4682236")

    filter_type = DuckDBFilter(indices, region, "contains")

    sql_query = DuckdbTemplate(
        ibd_segment_file=make_query_statement,
        filterObj=filter_type,
        indices=indices,
        min_cm=3.0,
    ).get_network_filter(add_sample_filter=False)
    # We are going to sanitize the strings just because there can be issues with whitespace that we don't want to break the test
    normalized_generated_query = normalize_sql(sql_query.strip())
    normalized_expected_query = normalize_sql(expected_SQL.strip())

    assert (
        normalized_generated_query == normalized_expected_query
    ), f"Expected the query string to be\n{normalized_expected_query}\nInstead found the query\n{normalized_generated_query}\n"
