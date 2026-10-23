"""Module to facilitate parsing phenotype files (both binary and continuous)
using a functional @contextmanager pattern."""

from collections.abc import Generator
from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from typing import Any

import pandas as pd
from log import CustomLogger

logger: Logger = CustomLogger.get_logger(__name__)


def load_phenotype_df(
    filepath: Path | str, is_continuous: bool = False
) -> pd.DataFrame:
    """Validate path and load tabular phenotype data into a DataFrame.

    Parameters
    ----------
    filepath : Path | str
        Path to the phenotype file.
    is_continuous : bool, default False
        Whether the phenotype data is continuous. If False, NA values include -1/-1.0
        and missing values are filled with -1. If True, -1 is treated as valid numeric
        data and missing values remain NaN.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the phenotype data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    pd.errors.ParserError
        If pd.read_csv fails to parse the file.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"The file {filepath} was not found")

    try:
        if is_continuous:
            pheno_df = pd.read_csv(
                filepath,
                sep="\t",
                na_values=["na", "n/a", " ", "", "NA", "N/A", "nan", "NaN"],
            )
        else:
            pheno_df = pd.read_csv(
                filepath,
                sep="\t",
                na_values=["na", "n/a", "-1", "-1.0", " ", "", "NA", "N/A"],
            ).fillna(-1)

    except pd.errors.ParserError as e:
        logger.critical(e)
        logger.critical(
            f"Encountered the following error while trying to read in the phenotype matrix: {filepath}"  # noqa: E501
        )
        raise pd.errors.ParserError(
            f"Encountered the following error while trying to read in the phenotype matrix: {filepath}"  # noqa: E501
        )

    logger.verbose(
        f"Reading in {pheno_df.shape[1] - 1} phecodes for {pheno_df.shape[0]} individuals"  # noqa: E501
    )

    return pheno_df


def resolve_phenotype_columns(
    df: pd.DataFrame, phenotype_name: str | None = None
) -> list[str]:
    """Determine which phenotype columns in the DataFrame to process.

    Parameters
    ----------
    df : pd.DataFrame
        Phenotype DataFrame where the first column is the individual ID.
    phenotype_name : str | None, default None
        Specific phenotype name to keep. If None, all phenotype columns are kept.

    Returns
    -------
    list[str]
        List of column names to analyze.

    Raises
    ------
    ValueError
        If phenotype_name is specified but not found in df.columns.
    """
    if phenotype_name is not None and phenotype_name not in df.columns:
        logger.critical(
            f"The phenotype {phenotype_name} was not found in the phenotype file"
        )
        raise ValueError(
            f"The phenotype {phenotype_name} was not found in the phenotype file"
        )
    elif phenotype_name is not None:
        return [phenotype_name]
    else:
        return list(df.columns[1:])


def parse_binary_matrix(
    df: pd.DataFrame, columns: list[str]
) -> tuple[dict[str, dict[str, set[str]]], list[str]]:
    """Generate case, control, and exclusion sets for binary phenotypes.

    Parameters
    ----------
    df : pd.DataFrame
        Phenotype DataFrame where the first column is the individual ID.
    columns : list[str]
        Phenotype column names to process.

    Returns
    -------
    tuple[dict[str, dict[str, set[str]]], list[str]]
        A dictionary mapping each phenotype to sets of 'cases', 'controls',
        and 'excluded' individual IDs, and a list of all cohort IDs.
    """
    grids = df.iloc[:, 0].astype(str)
    phenotype_dict: dict[str, dict[str, set[str]]] = {}

    for phecode_name, phenotyping_status in df.loc[:, columns].items():
        cases = set(grids[phenotyping_status[phenotyping_status == 1].index].unique())
        controls = set(
            grids[phenotyping_status[phenotyping_status == 0].index].unique()
        )
        exclusions = set(
            grids[phenotyping_status[phenotyping_status == -1].index].unique()
        )

        phenotype_dict[phecode_name] = {
            "cases": cases,
            "controls": controls,
            "excluded": exclusions,
        }

        logger.info(
            f"For PheCode, {phecode_name}, identified {len(cases)} cases, "
            f"{len(controls)} controls, and {len(exclusions)} exclusions"
        )

    return phenotype_dict, grids.values.tolist()


def parse_continuous_matrix(
    df: pd.DataFrame, columns: list[str]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Generate continuous measurement dictionaries for each phenotype.

    Parameters
    ----------
    df : pd.DataFrame
        Phenotype DataFrame where the first column is the individual ID.
    columns : list[str]
        Phenotype column names to process.

    Returns
    -------
    tuple[dict[str, dict[str, Any]], list[str]]
        A dictionary mapping each phenotype name to a dictionary with:
        - 'values': dict[str, float] mapping individual IDs to continuous values
        - 'excluded': set[str] of individual IDs with missing / NaN measurements
        And a list of all cohort IDs.
    """
    grids = df.iloc[:, 0].astype(str)
    phenotype_dict: dict[str, dict[str, Any]] = {}

    for pheno_name, series in df.loc[:, columns].items():
        numeric_series = pd.to_numeric(series, errors="coerce")
        valid_mask = numeric_series.notna()
        nan_mask = ~valid_mask

        valid_grids = grids[valid_mask]
        valid_values = numeric_series[valid_mask].astype(float)
        values_dict = dict(zip(valid_grids, valid_values))

        excluded_set = set(grids[nan_mask].unique())

        phenotype_dict[pheno_name] = {
            "values": values_dict,
            "excluded": excluded_set,
        }

        logger.info(
            f"For Continuous Phenotype, {pheno_name}, identified {len(values_dict)} "
            f"measured individuals and {len(excluded_set)} exclusions"
        )

    return phenotype_dict, grids.values.tolist()


@contextmanager
def open_phenotype_file(
    filepath: Path | str,
    phenotype_name: str | None = None,
    is_continuous: bool = False,
) -> Generator[tuple[dict[str, Any], list[str]], None, None]:
    """Context manager to read and parse phenotype files (binary or continuous).

    Parameters
    ----------
    filepath : Path | str
        Path to the phenotype file.
    phenotype_name : str | None, default None
        Specific phenotype to analyze. If None, all phenotypes in the file are processed.
    is_continuous : bool, default False
        Whether to parse the file for continuous phenotypes (True) or binary (False).

    Yields
    ------
    tuple[dict[str, Any], list[str]]
        Tuple containing the phenotype dictionary (case/control sets for binary,
        or values/exclusions for continuous) and the list of all cohort IDs.
    """
    df = load_phenotype_df(filepath, is_continuous=is_continuous)
    cols = resolve_phenotype_columns(df, phenotype_name)

    if is_continuous:
        phenotype_data, cohort_ids = parse_continuous_matrix(df, cols)
    else:
        phenotype_data, cohort_ids = parse_binary_matrix(df, cols)

    try:
        yield phenotype_data, cohort_ids
    finally:
        logger.verbose("Finished reading in individuals from the phenotype file")
