from pathlib import Path
from drive.models import IbdFileIndices
from .loci_filters import FilterProtocol
from log import CustomLogger

logger = CustomLogger.get_logger(__name__)


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
        SELECT DISTINCT
            t.*
        FROM read_csv(
            '{self.ibd_file}',
            delim='\t',
            header=False,
            columns={{
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
