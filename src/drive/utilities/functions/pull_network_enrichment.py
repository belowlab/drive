from argparse import Namespace
from pathlib import Path
import gzip
import sys
from log import CustomLogger
from typing import TextIO, BinaryIO
from collections.abc import Callable

logger = CustomLogger.get_logger(__name__)


def read_network_ids(networks_file: Path) -> set[str]:
    """read in the different network ids that we wish to pull enrichment values for

    Parameters
    ----------
    networks_file : Path
        tab separated text file provided by the user where each row
        represents a network that we wish to pull enrichment results
        for. This file should not have a header. If a header is in
        the file then it will be treated like a network id and a warning
        will be displayed later in the program when the "header id"
        is not found in the DRIVE results file

    Returns
    -------
    set[str]
        returns a list of networks ids that we wish to keep
    """
    networks = set()

    with open(networks_file, "r", encoding="utf-8") as networks_fh:
        for line in networks_fh:
            networks.add(line.strip())

    return networks


results_header_indices = list[tuple[str, int]]


def parse_header(file_header: str) -> results_header_indices:
    """Parse the drive header so that we have the indices for each p-value column

    Parameters
    ----------
    file_header : str
        header from the output file from DRIVE.

    Returns
    -------
    results_header_indices
        list of tuples that give the column name and the indices for every column
        that list the different enrichment p-values
    """
    col_indices = []

    split_header = file_header.strip().split("\t")

    for indx, element in enumerate(split_header):
        if element.endswith("_pvalue") and element != "min_pvalue":
            col_indices.append((element.removesuffix("_pvalue"), indx))

    return col_indices


def gather_pvalues(
    results_str: list[str], indice_list: results_header_indices
) -> dict[str, str]:
    """gather all of the different pvalues for a network so that we can write them to a file

    Parameters
    ----------
    results_str : list[str]
        list of all the values in a row from the DRIVE file

    indice_list : results_header_indices
        list of tuples where each value gives the indices of
        the pvalues for a certain phecode

    Returns
    -------
    dict[str, str]
        dictionary where the key is the phecode and the value
        is the pvalue of interest. Since we are immediately
        writing these to a file we are just going to keep them
        as strings and not convert the pvalues back into a float
    """
    phecode_pvalues = {}

    for phecode, phecode_indx in indice_list:
        phecode_pvalues[phecode] = results_str[phecode_indx]

    return phecode_pvalues


def determine_reader(results_path: Path) -> Callable[..., TextIO | BinaryIO]:
    """abstraction that decides whether to return a normal open function
    or gzip.open based on file type

    Parameters
    ----------
    results_path : Path
        Filename from the DRIVE analysis. This file can be
        compressed with GZIP or uncompressed

    Returns
    -------
    Callable[..., TextIO | BinaryIO]
        returns the open function if the file is not compressed
        and gzip.open function if the file is compressed
    """
    return gzip.open if results_path.suffix == ".gz" else open


def gather_drive_files(results_path: Path) -> list[Path]:
    """Gathers all of the files from the DRIVE analysis into a list

    Parameters
    ----------
    results_path : Path
        either a filepath to the output file from DRIVE or a directory
        which contains all of the output files from DRIVE. This function
        assumes that these files have the suffix 'drive_networks.txt'.

    Returns
    -------
    list[Path]
        returns a list containing the different files. If the results_path
        variable refers to a single file then this list will be of size 1

    Raises
    ------
    ValueError | FileNotFoundError
        raises a ValueError if no files with the suffix 'drive_networks.txt'
        are found within the provided directory. Raises a FileNotFoundError
        if the results_path variable doesn't exist
    """

    if not results_path.exists():
        raise FileNotFoundError(f"The path, {results_path}, does not exist.")
    elif results_path.is_dir():
        drive_files = list(results_path.glob("*drive_networks.txt"))
        # If there are no uncompressed files then we should look for compressed files
        if len(drive_files) == 0:
            logger.warning(
                "No uncompressed DRIVE results files found. Searching for gzipped compressed output files"
            )
            drive_files = list(results_path.glob("*drive_networks.txt.gz"))
            if len(drive_files) == 0:
                raise ValueError(
                    f"There were no drive files found in the directory: {results_path}. We are assuming that all the output files from DRIVE still have the same suffix 'drive_networks.txt'. Please make sure these files with this suffix are present"
                )
    else:
        drive_files = [results_path]

    return drive_files


def pull_network_enrichment(args: Namespace) -> None:
    """pull the enrichment results for networks of interest and write to a file.

    Parameters
    ----------
    args : Namespace
        The namespace that all the user parameters are read into at the
        start of the programs runtime

    """
    # Create a structure that list which networks we want to gather results for
    if not args.network_id:
        network_ids = read_network_ids(args.networks_file)
    else:
        # This is a set
        network_ids = {args.network_id}

    # The user can pass either a directory or a file as the input. The following
    # function will gather all of these files together
    drive_files = gather_drive_files(args.results_file)

    # This dictionary will hold the results that we care about. This will
    # be a nested dictionary where the outer key is the network id, the
    # inner key is the phecode id, and the values are the pvalues for each
    # phecode
    pvalues = {}
    for result_file in drive_files:
        # We need to create a set that defines what networks we need to find in the file
        remaining_networks = set(network_ids)
        reader = determine_reader(result_file)
        with reader(result_file, "rt") as results_fh:
            header = results_fh.readline()

            phecode_indices = parse_header(header)

            if not phecode_indices:
                logger.warning(
                    f"No phecode enrichment p-value columns were found in the header of {result_file}."
                )

            for line in results_fh:
                split_row = line.strip().split("\t")

                clst_id = split_row[0]
                if clst_id in remaining_networks:

                    network_pvalues = gather_pvalues(split_row, phecode_indices)

                    pvalues.setdefault(clst_id, {}).update(network_pvalues)
                    remaining_networks.remove(clst_id)

                    if not remaining_networks:
                        break

    if not pvalues:
        logger.warning(
            f"None of the provided network IDs were found in {args.results_file}."
        )
        sys.exit(1)
    elif remaining_networks:
        logger.warning(
            f"The following network IDs were not found in {args.results_file}: {', '.join(sorted(remaining_networks))}"
        )

    # now lets also abstract away the writer in case the user wishes to write the output
    # to a gzip file
    writer = open

    if args.output.suffix == ".gz":
        writer = gzip.open

    with writer(args.output, "wt") as output_fh:
        output_fh.write("network_id\tphecode_id\tphecode_pvalue\n")
        for network_id, network_pvalues in pvalues.items():
            for phecode, pvalue in network_pvalues.items():
                output_fh.write(f"{network_id}\t{phecode}\t{pvalue}\n")
