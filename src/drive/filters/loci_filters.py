import polars as pl
from pandas import DataFrame
from typing import Callable, Protocol
from log import CustomLogger

from drive.models import Genes, IbdFileIndices

logger = CustomLogger.get_logger(__name__)

# The following filters control behavior for how to filter to 
# specific IBD segments that overlap or contain the region of 
# interest. Everything that implements the FilterProtocol will have this as an overarching 
class FilterProtocol(Protocol):
    """each implementation will choose how to implement the filters but they should have a method to set them"""
    def set_filter(self, filter_options: str) -> Callable:
        ...

class PandasFilter(FilterProtocol):
    def __init__(self, indices: IbdFileIndices, target_gene: Genes, filter_type: str) -> None:
        self.indices = indices
        self.target_gene = target_gene
        self.filter: Callable = self.set_filter(filter_type)
    
    def contains_filter(self, data_chunk: DataFrame, min_cm: int) -> DataFrame:
        """Method that will filter the ibd file on four conditions: Chromosome number is the same, segment start position is <= target start position, segment end position is >= to the start position, and the size of the segment is >= to the minimum centimorgan threshold.

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        min_cm : int
            centimorgan threshold

        Returns
        -------
        pd.DataFrame
            returns the filtered dataframe

        Raises
        ------
        ValueError
            raises a ValueError if the target chromosome number is not
            found within the provided IBD file. This situation will
            lead to a error later in the program which is why the
            exception is raised. It is assumed to be due the user
            providing the incorrect file by accident
        """  # noqa: E501
        # We are going to filter the data and then make a copy
        # of it to return so that we don't get the
        # SettingWithCopyWarning

        return data_chunk[
            (data_chunk[self.indices.str_indx] <= self.target_gene.start)
            & (data_chunk[self.indices.end_indx] >= self.target_gene.end)
            & (data_chunk[self.indices.cM_indx] >= min_cm)
        ].copy()

    def overlaps_filter(self, data_chunk: DataFrame, min_cm: int) -> DataFrame:
        """Method that will filter the ibd file on four conditions: Chromosome number is the same, segment start position is <= target start position, segment end position is >= to the start position, and the size of the segment is >= to the minimum centimorgan threshold.

        Parameters
        ----------
        data_chunk : pd.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        min_cm : int
            centimorgan threshold

        Returns
        -------
        pd.DataFrame
            returns the filtered dataframe

        Raises
        ------
        ValueError
            raises a ValueError if the target chromosome number is not
            found within the provided IBD file. This situation will
            lead to a error later in the program which is why the
            exception is raised. It is assumed to be due the user
            providing the incorrect file by accident
        """  # noqa: E501

        # We are going to filter the data and then make a copy
        # of it to return so that we don't get the
        # SettingWithCopyWarning
        return data_chunk[
            (
                (
                    (data_chunk[self.indices.str_indx] <= int(self.target_gene.start))
                    & (data_chunk[self.indices.end_indx] >= int(self.target_gene.start))
                )
                | (
                    (data_chunk[self.indices.str_indx] >= int(self.target_gene.start))
                    & (data_chunk[self.indices.end_indx] <= int(self.target_gene.end))
                )
                | (
                    (data_chunk[self.indices.str_indx] <= int(self.target_gene.end))
                    & (data_chunk[self.indices.end_indx] >= int(self.target_gene.end))
                )
            )
            & (data_chunk[self.indices.cM_indx] >= min_cm)
        ].copy()

    def set_filter(self, filter_options: str) -> Callable:
        """Method to determine how the user wishes to filter the IBD segments file

        Parameters
        ----------
        filter_option : str
            string that represents the user's choice for how to filter the ibd segments.
            If the user chooses 'contains' the only segments that contain the entire
            region are kept. If the user chooses 'overlaps' then segments that overlap
            at all with the target region are kept.
        """
        assert filter_options in {
            "contains",
            "overlaps",
        }, "The filter option provided is invalid. Valid options are 'contains' or 'overlaps'. This error indicates that the argument validation in the parser is not working correctly or the program has been updated with additional filter types and this code was not updated accordingly"

        filters = {"contains": self.contains_filter, "overlaps": self.overlaps_filter}

        return filters[filter_options]



class PolarsFilter(FilterProtocol):

    def __init__(
        self, indices: IbdFileIndices, target_gene: Genes, filter_type: str
    ) -> None:
        self.indices = indices
        self.target_gene = target_gene
        self.filter: Callable = self.set_filter(filter_type)

    def contains_filter(self, data_chunk: pl.LazyFrame, min_cm: float) -> pl.LazyFrame:
        """
        This method works for both DataFrame (eager) and LazyFrame (lazy).
        When passed a LazyFrame, it adds a filter node to the query plan.
        """
        start_col = pl.col(self.indices.str_indx)
        end_col = pl.col(self.indices.end_indx)
        cm_col = pl.col(self.indices.cM_indx)

        exp = (
            (start_col <= self.target_gene.start)
            & (end_col >= self.target_gene.end)
            & (cm_col >= min_cm)
        )
        return data_chunk.filter(exp)

    def overlaps_filter(self, data_chunk: pl.LazyFrame, min_cm: float) -> pl.LazyFrame:
        """Method that will filter the ibd file on four conditions: Chromosome number is the same, segment start position is <= target start position, segment end position is >= to the start position, and the size of the segment is >= to the minimum centimorgan threshold.

        Parameters
        ----------
        data_chunk : pl.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        min_cm : int
            centimorgan threshold

        Returns
        -------
        pd.DataFrame
            returns the filtered dataframe

        Raises
        ------
        ValueError
            raises a ValueError if the target chromosome number is not
            found within the provided IBD file. This situation will
            lead to a error later in the program which is why the
            exception is raised. It is assumed to be due the user
            providing the incorrect file by accident
        """  # noqa: E501

        # Polars lazy filtering using column expressions and dictionary access
        start_col = pl.col(self.indices.str_indx)
        end_col = pl.col(self.indices.end_indx)
        cm_col = pl.col(self.indices.cM_indx)

        expr = (
            (
                (start_col <= int(self.target_gene.start))
                & (end_col >= int(self.target_gene.start))
            )
            | (
                (start_col >= int(self.target_gene.start))
                & (end_col <= int(self.target_gene.end))
            )
            | (
                (start_col <= int(self.target_gene.end))
                & (end_col >= int(self.target_gene.end))
            )
        ) & (cm_col >= min_cm)

        return data_chunk.filter(expr)

    def set_filter(self, filter_options: str) -> Callable:
        """Method that will set the filter type for the filtering object

        Parameters
        ----------
        filter_options : str
            string that indicates which type of filtering to use.
            Options are 'contains' or 'overlaps'. We know for certain that this value should be either

        Raises
        ------
        AssertionError
            raises a ValueError if the user provides an invalid filter
            option
        """
        assert filter_options in {
            "contains",
            "overlaps",
        }, "The filter option provided is invalid. Valid options are 'contains' or 'overlaps'. This error indicates that the argument validation in the parser is not working correctly or the program has been updated with additional filter types and this code was not updated accordingly"

        filters = {"contains": self.contains_filter, "overlaps": self.overlaps_filter}

        return filters[filter_options]
    
class DuckDBFilter(FilterProtocol):

    def __init__(
        self, indices: IbdFileIndices, target_gene: Genes, filter_type: str
    ) -> None:
        self.indices = indices
        self.target_gene = target_gene
        self.filter: Callable = self.set_filter(filter_type)

    def contains_filter(self) ->str:
        """
        This method works for both DataFrame (eager) and LazyFrame (lazy).
        When passed a LazyFrame, it adds a filter node to the query plan.
        """
        return f"""
            (t.{self.indices.str_indx} <= {self.target_gene.start} AND t.{self.indices.end_indx} >= {self.target_gene.end})
        """

    def overlaps_filter(self) -> str:
        """Method that will filter the ibd file on four conditions: Chromosome number is the same, segment start position is <= target start position, segment end position is >= to the start position, and the size of the segment is >= to the minimum centimorgan threshold.

        Parameters
        ----------
        data_chunk : pl.DataFrame
            chunk of the ibdfile. The size of this chunk is
            determined by the chunksize argument to
            pd.read_csv. This value is currently set to 100,000.

        min_cm : int
            centimorgan threshold

        Returns
        -------
        pd.DataFrame
            returns the filtered dataframe

        Raises
        ------
        ValueError
            raises a ValueError if the target chromosome number is not
            found within the provided IBD file. This situation will
            lead to a error later in the program which is why the
            exception is raised. It is assumed to be due the user
            providing the incorrect file by accident
        """  # noqa: E501

        # Polars lazy filtering using column expressions and dictionary access
        return f"""
            (
                (t.{self.indices.str_indx} <= {self.target_gene.start} AND t.{self.indices.end_indx} >= {self.target_gene.start}) OR
                (t.{self.indices.str_indx} >= {self.target_gene.start} AND t.{self.indices.end_indx} <= {self.target_gene.end}) OR
                (t.{self.indices.str_indx} <= {self.target_gene.end}   AND t.{self.indices.end_indx} >= {self.target_gene.end})
            )
        """

    def set_filter(self, filter_options: str) -> Callable:
        """Method that will set the filter type for the filtering object

        Parameters
        ----------
        filter_options : str
            string that indicates which type of filtering to use.
            Options are 'contains' or 'overlaps'. We know for certain that this value should be either

        Raises
        ------
        AssertionError
            raises a ValueError if the user provides an invalid filter
            option
        """
        assert filter_options in {
            "contains",
            "overlaps",
        }, "The filter option provided is invalid. Valid options are 'contains' or 'overlaps'. This error indicates that the argument validation in the parser is not working correctly or the program has been updated with additional filter types and this code was not updated accordingly"

        filters = {"contains": self.contains_filter, "overlaps": self.overlaps_filter}

        return filters[filter_options]