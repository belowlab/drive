from pathlib import Path
from drive.models import IbdFileIndices
from .loci_filters import FilterProtocol
from log import CustomLogger
import gzip
from contextlib import contextmanager
from typing import IO
from collections.abc import Generator

logger = CustomLogger.get_logger(__name__)


@contextmanager
def open_ibdfile(file_path: Path) -> Generator[IO[str], None, None]:
    """Context manager abstraction to open gzipped or raw text files.

    Parameters
    ----------
    file_path : Path
        Path to IBD segments file.
    """
    if file_path.suffix == ".gz":
        with gzip.open(file_path, mode="rt", encoding="utf-8") as f:
            yield f
    else:
        with open(file_path, mode="r", encoding="utf-8") as f:
            yield f


class DuckdbTemplate:

    def __init__(
        self,
        ibd_segment_file: Path,
        filterObj: FilterProtocol,
        indices: IbdFileIndices,
        min_cm: float,
    ) -> None:
        self.ibd_file = ibd_segment_file
        self.filter = filterObj
        self.indices = indices
        self.min_cm = min_cm

    def sniff_columns(self) -> list[str]:
        """parse the first line of the file to determine how many columns are
        in the file

        Returns
        -------
        list[str]
            returns a list of column names. The IBD files generally don't have
            a header so this will just pad the word 'column' with the number
            indice
        """
        with open_ibdfile(self.ibd_file) as ibd_fh:
            first_line = ibd_fh.readline().split("\t")
        return [f"column{i}" for i, _ in enumerate(first_line)]

    def get_network_filter(self, add_sample_filter: bool) -> str:
        """generate the SQL query for when we want to filter the IBD file for the network analysis. Here we are just filtering the file on the following conditions: 1) samples either overlap or contain the locus of interest, 2) segments are longer than a minimum threshold, and 3) if we want to keep the files (This 3rd point can be turned on or off)

        Parameters
        ----------
        add_sample_filter : bool
            boolean flag indicating whether or not we need to filter the dataset for certain samples

        Returns
        -------
        str
            returns the formatted query string
        """
        # for clarity we are goin to write out all of the conditions here
        if add_sample_filter:
            condition = [
                f"t.{self.indices.id1_indx} IN (SELECT IDs FROM ids_df)",
                f"t.{self.indices.id2_indx} IN (SELECT IDs FROM ids_df)",
                f"{self.filter.filter()}",
                f"t.{self.indices.cM_indx} >= {self.min_cm}",
            ]
        else:
            condition = [
                f"{self.filter.filter()}",
                f"t.{self.indices.cM_indx} >= {self.min_cm}",
            ]

        condition_str = " AND ".join(condition)

        query_str = f"""
        SELECT
            t.*
        FROM read_csv(
            '{self.ibd_file}',
            delim='\t',
            header=False,
            names={self.sniff_columns()},
            types={{
                '{self.indices.id1_indx}':'VARCHAR',
                '{self.indices.hap1_indx}':'VARCHAR',
                '{self.indices.id2_indx}':'VARCHAR',
                '{self.indices.hap2_indx}':'VARCHAR',
                '{self.indices.chr_indx}':'VARCHAR',
                '{self.indices.str_indx}':'BIGINT',
                '{self.indices.end_indx}':'BIGINT',
                '{self.indices.cM_indx}':'DOUBLE'
            }}
        ) as t
        WHERE
            {condition_str}
        """
        logger.debug(f"Returning the following query_str:\n{query_str}\n")

        return query_str
