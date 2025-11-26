from pandas import DataFrame
import polars as pl
from datetime import datetime
from log import CustomLogger
import duckdb
from drive.models import IbdFileIndices


logger = CustomLogger.get_logger(__name__)


def add_haplotype_id(
    data: DataFrame,
    ind_id_indx: int,
    phase_col_indx: int,
    col_name: str,
    ibd_file_format: str,
) -> None:
    """function to add the haplotype id to the dataframe"""
    match ibd_file_format:
        case "hapibd" | "rapid":
            data.loc[:, col_name] = (
                data[ind_id_indx] + "." + data[phase_col_indx].astype(str)
            )
        case "germline" | "ilash":
            data.loc[:, col_name] = data[phase_col_indx]
        case _:
            assert ibd_file_format in [
                "hapibd",
                "ilash",
                "germline",
                "rapid",
            ], f"The ibd format value provided, {ibd_file_format}, is not one of the allowed values ['hapibd', 'ilash', 'germline', 'rapid']"


def _get_unique_id_count(df: pl.DataFrame, col1_name: str, col2_name: str) -> int:
    """calculate the number of unique ids across the two columns

    Parameters
    ----------
    df : pl.DataFrame
        dataframe that has the ibd segments

    col1_name : str
        name of the first column to get values from

    col2_name : str
        name of the second column to get values from

    Returns
    -------
    int
        returns the number of unique values across both
        columns
    """
    return pl.concat(
        [
            df.select(pl.col(col1_name).alias("id")),
            df.select(pl.col(col2_name).alias("id")),
        ]
    ).n_unique()


def filter_ibd_file(
    sql_query: str, keep_df: pl.DataFrame, indices: IbdFileIndices
) -> pl.DataFrame:
    """This function will produce the following basic filtering: 1) min_cM threshold, 2) keep samples 3) overlaps or contains locus of interest

    Parameters
    ----------
    sql_query : str
        query string that will be used in the duckdb filtering

    keep_df : pl.DataFrame
        dataframe that has one column named IDs. This dataframe
        represents all of the ids to keep in the analysis

    Returns
    -------
    pl.DataFrame
        returns a polars dataframe after all of the filtering
    """

    start_time = datetime.now()

    conn = duckdb.connect()

    conn.register("ids_df", keep_df)

    logger.info(
        f"filtering the ibd segments to only include {keep_df.shape[0]} participants"
    )

    filtered_df = conn.execute(sql_query).pl()

    samples_with_segments = _get_unique_id_count(
        filtered_df, indices.id1_indx, indices.id2_indx
    )

    logger.info(
        f"Identified IBD segments for {samples_with_segments}/{keep_df.shape[0]} sample in the cohort"
    )

    filtered_df = (
        filtered_df.with_columns(
            (pl.col(indices.id1_indx) + pl.col(indices.hap1_indx)).alias("hapid1"),
            (pl.col(indices.id2_indx) + pl.col(indices.hap2_indx)).alias("hapid2"),
        )
        .drop(
            [indices.id1_indx, indices.hap1_indx, indices.id2_indx, indices.hap2_indx]
        )
        .unique()
    )

    logger.verbose(
        f"identified {_get_unique_id_count(filtered_df, "hapid1", "hapid2")}"
    )

    logger.info(f"read in {filtered_df.shape[0]} ibd segments for the cohort")

    end_time = datetime.now()

    logger.verbose(
        f"Finished reading in the IBD file. Time spent reading file: {end_time - start_time}"
    )

    return filtered_df
