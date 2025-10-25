"""Module to faciliate the user in parsing the phenotype file by incorporating multiple
ecodings, separators, and by handling multiple errors."""

from logging import Logger
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, TypeVar, Union

import pandas as pd
from log import CustomLogger

logger: Logger = CustomLogger.get_logger(__name__)

# creating a type annotation for the PhenotypeFileParser class
T = TypeVar("T", bound="PhenotypeFileParser")

PhenotypeInfo = TypeVar("PhenotypeInfo", bound=dict)


class PhenotypeFileParser:
    """Parser used to read in the phenotype file. This will allow use to account for
    different delimiters in files as well as catch errors."""

    def __init__(
        self,
        filepath: Union[Path, str],
        phenotype_name: Optional[str] = None,
        output_dir: Path = "./",
    ) -> None:
        """Initialize the PhenotypeFileParser class.

        Parameters
        ----------
        filepath : Path | str
            filepath to the phenotype file that has case control status for individuals

        phenotype_name : str
            Phenotype name that can be used specify a specific column in a
            phenotype matrix if the user only wants ot focus on 1 phenotype.

        output_dir : Path
            path that output will be written to. This value serves more as state for the
            object that can be used in optional file operations. Default value is the current
            directory.

        Raises
        ------
        FileNotFoundError
        """
        self.specific_phenotype: str | None = phenotype_name
        self.output_dir: Path = output_dir
        # we are going to make sure the filepath variable is a
        # PosixPath
        filepath = Path(filepath)

        # now we are going to try to create an attribute for
        # the input file
        if not filepath.exists():
            raise FileNotFoundError(f"The file {filepath} was not found")
        else:
            self.file: Path = filepath

    def __enter__(self) -> T:
        """Open the input file. Method determines the appropriate file type and open
        the file. Method is called automatically by the context manager.

        Raises
        ------
        pd.errors.ParserError
            Raised if the program encounters any error while trying to read in the
            phenotype matrix using pd.read_csv
        """
        try:
            pheno_df = pd.read_csv(
                self.file,
                sep="\t",
                na_values=["na", "n/a", "-1", "-1.0", " ", "", "NA", "N/A"],
            ).fillna(-1)

        except pd.errors.ParserError as e:
            logger.critical(e)
            logger.critical(
                f"Encountered the following error while trying to read in the phenotype matrix: {self.file}"  # noqa: E501
            )
            raise pd.errors.ParserError(
                f"Encountered the following error while trying to read in the phenotype matrix: {self.file}"  # noqa: E501
            )

        self.phenotype_df = pheno_df

        logger.verbose(
            f"Reading in {self.phenotype_df.shape[1] - 1} phecodes for {self.phenotype_df.shape[0]} individuals"  # noqa: E501
        )  # noqa: E501

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close the resource when it is not longer being used. Used by the context
        manager."""
        logger.verbose("Finished reading in individuals from the phenotype file")

    def _generate_columns_to_keep(self) -> List[str]:
        """determines which columns in the phecode file to use

        Returns
        -------
        List[str]
        returns a list of strings. If the user specified a specific phecode then
        it returns every phecode otherwise it returns a single phecode in a list

        Raises
        ------
        ValueError
            if the specified PheCode is not found in the phenotype file then an error is
            logged and raised
        """
        if (
            self.specific_phenotype is not None
            and self.specific_phenotype not in self.phenotype_df.columns
        ):  # noqa: E501
            logger.critical(
                f"The phenotype {self.specific_phenotype} was not found in the phenotype file"  # noqa: E501
            )  # noqa: E501
            raise ValueError(
                f"The phenotype {self.specific_phenotype} was not found in the phenotype file"  # noqa: E501
            )  # noqa: E501
        elif self.specific_phenotype is not None:
            return [self.specific_phenotype]
        else:
            return list(self.phenotype_df.columns[1:])

    def _process_matrix(
        self, columns: List[str]
    ) -> Tuple[Dict[str, Dict[str, Set[str]]], List[str]]:
        """Function that will generate a dictionary where the keys are
        phenotypes and the values are lists of the cases/exclusions/controls

        Parameters
        ----------
        columns : List[str]
            list of columns from the phenotype matrix. If the user provides
            a specific phenotype then this list will be of size one, otherwise it will
            be the size of the number of phecodes in the file.

        Returns
        -------
        Tuple[Dict[str, Dict[str, Set[str]]], List[str]]
            returns a tuple with three elements. The first element is a
            dictionary where the keys are phenotypes. Values are
            dictionaries where the keys are 'cases' or 'controls' or
            'excluded' and values are list of ids. The second element is
            a dictionary that maps the index of the phenotype in the
            header line to the phenotype name. The third element is the
            separator string
        """

        # we need to create the dictionary that will have the case/control/exclusion
        # ids for each phecode
        phenotype_dict = {phecode: None for phecode in columns}

        # we need to create a dictionary that will map the index of the phenotype

        # we ultimately are going to just want to filter this grids series
        grids = self.phenotype_df.iloc[:, 0].astype(str)

        # We will pull out values for each phenotype to determine the cases/controls/
        # exclusions
        for phecode_name, phenotyping_status in self.phenotype_df.loc[
            :, columns
        ].items():
            cases = set(
                grids[phenotyping_status[phenotyping_status == 1].index].unique()
            )

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
                f"For PheCode, {phecode_name}, identified {len(phenotype_dict[phecode_name]['cases'])} cases, {len(phenotype_dict[phecode_name]['controls'])} controls, and {len(phenotype_dict[phecode_name]['excluded'])} exclusions"
            )  # noqa: E501
        return phenotype_dict, grids.values.tolist()

    def parse_cases_and_controls(
        self,
    ) -> Tuple[Dict[str, Dict[str, Set[str]]], Dict[int, str]]:
        """Generate a list for cases, controls, and excluded individuals.

        Returns
        -------
        Tuple[Dict[str, Dict[str, Set[str]]], List[str]]
            returns a tuple where the first element is a dictionary where
            the keys are the phenotypes and the values are dictionary of
            the case/controls/excluded individuals lists. The second
            element is a list of all grids from the file to be used as a
            cohort
        """

        cols_to_keep = self._generate_columns_to_keep()

        phenotyping_dictionary, cohort_ids = self._process_matrix(cols_to_keep)

        return phenotyping_dictionary, cohort_ids

    def filter_cases_and_controls(
        self,
        phenotype_dictionary: dict[str, dict[str, set[str]]],
        keep_id_list: set[str],
        record_frequencies: bool,
    ) -> dict[str, dict[str, set[str]]]:
        """filter the case/control/exclusion list for each phenotype to only
        individuals in networks. This will only be used if the user enables
        the experimental feature to calculate phenotype frequencies only using
        the related set

        Parameters
        ----------
        phenotype_dictionary : dict[str, dict[str, set[str]]]
            dictionary where the outer keys are the phenotypes of interest and
            the values are a dictionary containing list of cases, controls, and
            exclusions for each phenotype

        keep_id_list : set[str]
            Set containing the ids to filter each phecode to

        record_frequencies : bool
            whether to record the phenotype frequencies of the cohort that consist
            of only related individuals. This file will be written to the output directory specified by self.output_dir

        Returns
        -------
        dict[str, dict[str, set[str]]]
            returns a dictionary where the keys are phecodes and the values are
            the case, control, and exclusions sets of individuals filtered to
            the individuals in the filter_id_list argument
        """
        logger.info(
            f"Filtering cases and controls for {len(phenotype_dictionary.keys())} phenotypes to only related individuals that were clustered into networks"
        )
        filtered_counts = {}

        for phenotype, phenotype_counts in phenotype_dictionary.items():
            inner_counts_dict = filtered_counts.setdefault(
                phenotype, {}
            )  # This will return the new dictionary counts
            for status_category, original_id_set in phenotype_counts.items():
                filtered_id_set = original_id_set.intersection(keep_id_list)
                inner_counts_dict[status_category] = filtered_id_set

        if record_frequencies:
            logger.info(
                f"Recording the phenotype counts for the cohort of related individuals to the file: {self.output_dir / "cohort_frequencies.txt"}"
            )
            with open(
                self.output_dir / "cohort_frequencies.txt", "w"
            ) as cohort_freq_fh:
                cohort_freq_fh.write(
                    "phecode\tcases\tcontrols\texclusions\tfrequency\n"
                )
                for phenotype, phenotype_counts in filtered_counts.items():
                    cohort_freq_fh.write(
                        f"{phenotype}\t{phenotype_counts.get("cases", "N/A")}\t{phenotype_counts.get("controls", "N/A")}\t{phenotype_counts.get("excluded", "N/A")}\t{phenotype_counts.get("cases")/phenotype_counts.get("controls")}\n"
                    )

        return filtered_counts
