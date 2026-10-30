import argparse
import gzip
from pathlib import Path
import sys
from typing import Callable, TextIO
from collections.abc import Generator
from contextlib import contextmanager

from log import CustomLogger
import polars as pl

from drive.filters import DuckDBFilter, DuckdbTemplate, filter_ibd_file
from drive.helper_funcs import open_writer, split_target_string
from drive.models import create_indices

logger = CustomLogger.get_logger(__name__)

NetworkMembers = dict[str, set[str]]
NetworkMembersMap = dict[str, NetworkMembers]
NetworkLoadResult = tuple[NetworkMembersMap, set[str]]


def determine_reader(file_path: Path) -> Callable:
    """Return gzip.open if file_path ends with .gz, otherwise return open."""
    return gzip.open if file_path.suffix == ".gz" else open


def read_network_ids(networks_file: Path) -> set[str]:
    """Read network IDs from a text or tab-separated file.

    Parameters
    ----------
    networks_file : Path
        Path to file containing network IDs (one per row).

    Returns
    -------
    set[str]
        Set of network IDs.
    """
    networks: set[str] = set()
    with open(networks_file, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped:
                # If tab-separated, take the first column
                networks.add(stripped.split("\t")[0])
    return networks


def load_network_members(
    drive_results_path: Path,
    target_network_ids: set[str],
) -> NetworkLoadResult:
    """Read the DRIVE results file and extract member IDs and haplotypes.

    Parameters
    ----------
    drive_results_path : Path
        Path to DRIVE results (*.drive_networks.txt or *.gz).
    target_network_ids : set[str]
        Set of network clstIDs to extract.

    Returns
    -------
    NetworkLoadResult
        Tuple containing:
        1. NetworkMembersMap: Mapping of clst_id -> {"samples": set[str], "haplotypes": set[str]}
        2. set[str]: Set of network IDs not found in the file.
    """
    found_networks: NetworkMembersMap = {}
    reader = determine_reader(drive_results_path)

    with reader(drive_results_path, "rt", encoding="utf-8") as fh:
        # Check header
        header = fh.readline()
        if not header:
            return found_networks, set(target_network_ids)

        for line in fh:
            split_line = line.strip().split("\t")
            if not split_line or len(split_line) < 8:
                continue

            clst_id = split_line[0]
            if clst_id in target_network_ids:
                samples = set(split_line[6].split(",")) if split_line[6] else set()
                haplotypes = set(split_line[7].split(",")) if split_line[7] else set()
                found_networks[clst_id] = {
                    "samples": samples,
                    "haplotypes": haplotypes,
                }

    missing_ids = target_network_ids - set(found_networks.keys())
    return found_networks, missing_ids


def get_header_columns(format_name: str, num_cols: int) -> list[str]:
    """Return standard header names prepended with clstID for known formats."""
    headers: dict[str, list[str]] = {
        "hapibd": ["clstID", "id1", "hap1", "id2", "hap2", "chr", "start", "end", "cM"],
        "rapid": ["clstID", "chr", "id1", "id2", "hap1", "hap2", "start", "end", "cM"],
        "germline": [
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
        ],
        "ilash": [
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
        ],
    }
    format_header = headers.get(format_name.lower())
    if format_header and len(format_header) == num_cols + 1:
        return format_header
    return ["clstID"] + [f"column{i}" for i in range(num_cols)]


def pull_network_segments(args: argparse.Namespace) -> None:
    """Pull pairwise IBD segments for network(s) of interest and write to file."""
    # Step 1: Collect target network IDs
    if args.network_id:
        target_network_ids: set[str] = {args.network_id}
    else:
        target_network_ids = read_network_ids(args.networks_file)

    logger.info(
        f"Attempting to pull pairwise segments for {len(target_network_ids)} network(s)."
    )

    # Step 2: Read DRIVE results file using fixed column indices
    found_networks, missing_ids = load_network_members(
        args.drive_file, target_network_ids
    )

    if not found_networks:
        logger.critical(
            f"None of the provided network IDs were found in {args.drive_file}."
        )
        sys.exit(1)

    if missing_ids:
        logger.warning(
            f"The following network IDs were not found in {args.drive_file}: "
            f"{', '.join(sorted(missing_ids))}"
        )

    # Step 3: Collect candidate sample IDs across all found networks
    cohort_ids: set[str] = set()
    for members in found_networks.values():
        cohort_ids.update(members["samples"])

    cohort_id_df = pl.DataFrame({"IDs": sorted(cohort_ids)})

    # Step 4: Configure DuckDB query and filter IBD segments
    indices = create_indices(args.format.lower())
    target_gene = split_target_string(args.target)
    segment_filter = DuckDBFilter(indices, target_gene, args.segment_overlap)

    sql_query = DuckdbTemplate(
        ibd_segment_file=args.ibd_file,
        filterObj=segment_filter,
        indices=indices,
        min_cm=args.min_cm,
    ).get_network_filter(add_sample_filter=True)

    filtered_ibd_df = filter_ibd_file(
        sql_query=sql_query,
        thread_count=args.threads,
        keep_df=cohort_id_df,
        indices=indices,
        max_memory=args.max_memory,
        temp_dir=args.temp_dir,
    )

    # Step 5 & 6: Mandatory haplotype-level filtering and output writing
    raw_cols = [c for c in filtered_ibd_df.columns if c not in ("hapid1", "hapid2")]
    header_cols = get_header_columns(args.format, len(raw_cols))

    total_segments_written = 0

    with open_writer(args.output) as out_fh:
        out_fh.write("\t".join(header_cols) + "\n")

        for clst_id, members in found_networks.items():
            network_haplotypes = members["haplotypes"]
            network_segments = filtered_ibd_df.filter(
                pl.col("hapid1").is_in(network_haplotypes)
                & pl.col("hapid2").is_in(network_haplotypes)
            )

            segment_count = network_segments.shape[0]
            logger.info(
                f"Network {clst_id}: identified {segment_count} pairwise segment(s)."
            )

            if segment_count > 0:
                raw_rows = network_segments.select(raw_cols).iter_rows()
                for row in raw_rows:
                    row_str = "\t".join(str(val) for val in row)
                    out_fh.write(f"{clst_id}\t{row_str}\n")
                    total_segments_written += 1

    logger.info(
        f"Successfully wrote {total_segments_written} pairwise segment(s) to {args.output}."
    )
