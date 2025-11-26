import polars as pl
from datetime import datetime
from log import CustomLogger
import duckdb
import sys
from drive.models import IbdFileIndices


logger = CustomLogger.get_logger(__name__)


def _add_haplotype_id(data: pl.DataFrame, indices: IbdFileIndices) -> pl.DataFrame:
    """function to add the haplotype id to the dataframe

    Parameters
    ----------
    data : pl.DataFrame
        polars dataframe that was read in with duckdb. It should have two columns
        for individual ids and then two columns representing the haplotype phase

    indices : IbdFileIndices
        namedtuple that holds the correct column name for different information in the file

    Returns
    -------
    pl.DataFrame
        returns the dataframe with two more columns representing ids for each haplotype

    Raises
    ------
    AssertionError
        if for some reason the ibd program name is not one of the four
        acceptable values then the program will throw an AssertionError and
        terminate because something has gone wrong at that point
    """
    match indices.prog_name:
        case "hapibd" | "rapid":
            hap1_expr = pl.format(
                "{}.{}", pl.col(indices.id1_indx), pl.col(indices.hap1_indx)
            )

            hap2_expr = pl.format(
                "{}.{}", pl.col(indices.id2_indx), pl.col(indices.hap2_indx)
            )

        case "germline" | "ilash":
            # Define logic for copying: Just select the columns
            hap1_expr = pl.col(indices.id1_indx)
            hap2_expr = pl.col(indices.id2_indx)
        case _:
            assert indices.prog_name in [
                "hapibd",
                "ilash",
                "germline",
                "rapid",
            ], f"The ibd format value provided, {indices.prog_name}, is not one of the allowed values ['hapibd', 'ilash', 'germline', 'rapid']"
            logger.critical(
                "unable to create haplotype ids even though . This behavior is unexpected and should be reported because it likely indicates there is a bug"
            )
            sys.exit(1)

    return data.with_columns(hap1_expr.alias("hapid1"), hap2_expr.alias("hapid2"))


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


def _check_for_no_segments(data: pl.DataFrame) -> None:
    """check if the dataframe is empty and logger a message and terminate program if it is

    Parameters
    ----------
    data : pl.DataFrame
        polars dataframe containing information about the IBD segments in the
        cohort
    """
    if data.is_empty():
        logger.critical(
            "There were no ibd segments found in the target loci once the file was read in"
        )
        sys.exit(0)


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

    if keep_df.shape[0]:
        conn.register("ids_df", keep_df)

        logger.info(
            f"filtering the ibd segments to only include {keep_df.shape[0]} participants"
        )
    try:
        filtered_df = conn.execute(sql_query).pl()
    except duckdb.InvalidInputException as e:
        logger.critical(
            f"Encountered the following exception while trying to run the following query:\nQUERY:\n{sql_query}\n.EXCEPTION:{e}\n"
        )
        sys.exit(1)

    samples_with_segments = _get_unique_id_count(
        filtered_df, indices.id1_indx, indices.id2_indx
    )

    if keep_df.shape[0]:
        logger.info(
            f"Identified IBD segments for {samples_with_segments}/{keep_df.shape[0]} sample in the cohort"
        )
    else:
        logger.info(
            f"Identified IBD segments for {samples_with_segments} samples in the cohort"
        )

    # we need to generate the haplotype ids and drop duplicated
    # rows or rows where the ids are the same (This shouldn't
    # happen). Then we can only keep the new hapid* columns
    logger.verbose("Creating ids for each each haplotype")

    filtered_df = _add_haplotype_id(data=filtered_df, indices=indices)
    # Now that we have the haplotype ids we can drop other columns
    filtered_df.drop([indices.hap1_indx, indices.hap2_indx]).filter(
        pl.col("hapid1") != pl.col("hapid2")
    ).unique()

    logger.verbose(
        f"identified {_get_unique_id_count(filtered_df, 'hapid1', 'hapid2')} haplotypes in the cohort"
    )

    logger.info(f"read in {filtered_df.shape[0]} ibd segments for the cohort")

    _check_for_no_segments(filtered_df)

    end_time = datetime.now()

    logger.verbose(
        f"Finished reading in the IBD file. Time spent reading file: {end_time - start_time}"
    )

    return filtered_df
