from dataclasses import dataclass
from typing import Protocol
from collections import namedtuple
from pandas import DataFrame

IbdFileIndices = namedtuple(
    "IbdFileIndices",
    [
        "id1_indx",
        "hap1_indx",
        "id2_indx",
        "hap2_indx",
        "chr_indx",
        "str_indx",
        "end_indx",
        "cM_indx",
    ],
)


# general protocol that defines that every class needs the get_haplotype_id method
class FileIndices(Protocol):
    def get_haplotype_id(
        self, data: DataFrame, ind_id_indx: int, phase_col_indx: int, col_name: str
    ) -> None: ...


@dataclass
class HapIBD(FileIndices):
    id1_indx: int = 0
    hap1_indx: int = 1
    id2_indx: int = 2
    hap2_indx: int = 3
    chr_indx: int = 4
    str_indx: int = 5
    end_indx: int = 6
    cM_indx: int = 7

    def get_haplotype_id(
        self, data: DataFrame, ind_id_indx: int, phase_col_indx: int, col_name: str
    ) -> None:
        data.loc[:, col_name] = (
            data[ind_id_indx] + "." + data[phase_col_indx].astype(str)
        )

    def __str__(self):
        """Custom string message used for debugging"""
        return f"HapIBD: id1_index={self.id1_indx}, id2_index={self.id2_indx}, haplotype_1_index={self.hap1_indx}, haplotype_2_index={self.hap2_indx}, chromosome_index={self.chr_indx}, start_position_index={self.str_indx}, end_position_index={self.end_indx}, centimorgan_index={self.cM_indx}"  # noqa: E501


@dataclass
class Germline(FileIndices):
    id1_indx: int = 0
    hap1_indx: int = 1
    id2_indx: int = 2
    hap2_indx: int = 3
    chr_indx: int = 4
    str_indx: int = 5
    end_indx: int = 6
    cM_indx: int = 10
    unit: int = 11

    def get_haplotype_id(
        self, data: DataFrame, ind_id_indx: int, phase_col_indx: int, col_name: str
    ) -> None:
        data.loc[:, col_name] = data[phase_col_indx]

    def __str__(self):
        """Custom string message used for debugging"""
        return f"Germline: id1_index={self.id1_indx}, id2_index={self.id2_indx}, haplotype_1_index={self.hap1_indx}, haplotype_2_index={self.hap2_indx}, chromosome_index={self.chr_indx}, start_position_index={self.str_indx}, end_position_index={self.end_indx}, centimorgan_index={self.cM_indx}, unit_index={self.unit}"  # noqa: E501


@dataclass
class iLASH(FileIndices):
    id1_indx: int = 0
    hap1_indx: int = 1
    id2_indx: int = 2
    hap2_indx: int = 3
    chr_indx: int = 4
    str_indx: int = 5
    end_indx: int = 6
    cM_indx: int = 9

    def get_haplotype_id(
        self, data: DataFrame, ind_id_indx: int, phase_col_indx: int, col_name: str
    ) -> None:
        data.loc[:, col_name] = data[phase_col_indx]

    def __str__(self):
        """Custom string message used for debugging"""
        return f"iLASH: id1_index={self.id1_indx}, id2_index={self.id2_indx}, haplotype_1_index={self.hap1_indx}, haplotype_2_index={self.hap2_indx}, chromosome_index={self.chr_indx}, start_position_index={self.str_indx}, end_position_index={self.end_indx}, centimorgan_index={self.cM_indx}"  # noqa: E501


@dataclass
class Rapid(FileIndices):
    id1_indx: int = 1
    hap1_indx: int = 3
    id2_indx: int = 2
    hap2_indx: int = 4
    chr_indx: int = 0
    cM_indx: int = 7
    str_indx: int = 5
    end_indx: int = 6

    def get_haplotype_id(
        self, data: DataFrame, ind_id_indx: int, phase_col_indx: int, col_name: str
    ) -> None:
        data.loc[:, col_name] = (
            data[ind_id_indx] + "." + data[phase_col_indx].astype(str)
        )

    def __str__(self):
        """Custom string message used for debugging"""
        return f"Rapid: id1_index={self.id1_indx}, id2_index={self.id2_indx}, haplotype_1_index={self.hap1_indx}, haplotype_2_index={self.hap2_indx}, chromosome_index={self.chr_indx}, start_position_index={self.str_indx}, end_position_index={self.end_indx}, centimorgan_index={self.cM_indx}"  # noqa: E501


def create_indices(ibd_file_format: str) -> FileIndices:
    """Factory method to generate the proper file indice object based on the ibd program

    Parameters
    ----------
    ibd_file_format: str
        string indicating what ibd program was used identify IBD segments. EX: hapibd,
        ilash, rapid, and germline. expects this value to be lower case

    Returns
    -------
    FileIndices
        returns an object that conforms to the FileIndices protocol. It will have the
        method getHAPID. It will also have the correct indices for the ibd program

    Raises
    ------
    ValueError
        Raises a value error if the user passes an ibd_file_format that is not hapibd,
        hap-ibd, germline, ilash, rapid
    """
    format_selector = {
        "germline": Germline(),
        "ilash": iLASH(),
        "hapibd": HapIBD(),
        "rapid": Rapid(),
    }

    return format_selector.get(ibd_file_format)


def generate_indices_v2(ibd_file_format: str) -> IbdFileIndices:
    """Factory method to generate the proper file indice object based on the ibd program

    Parameters
    ----------
    ibd_file_format: str
        string indicating what ibd program was used identify IBD segments. EX: hapibd,
        ilash, rapid, and germline. expects this value to be lower case

    Returns
    -------
    FileIndices
        returns an object that conforms to the FileIndices protocol. It will have the
        method getHAPID. It will also have the correct indices for the ibd program

    Raises
    ------
    AssertionError
        By this point in the program the ibd_file_format string
        should only be of values hapibd, germline, ilash, rapid. We
        will make sure this is the case and crash the program if it
        isn't because that would indicate unexpected behavior in the
        program
    """
    match ibd_file_format:
        case "germline":
            indices = [0, 1, 2, 3, 4, 5, 6, 10]
        case "hapibd":
            indices = [0, 1, 2, 3, 4, 5, 6, 7]
        case "ilash":
            indices = [0, 1, 2, 3, 4, 5, 6, 9]
        case "rapid":
            indices = [1, 3, 2, 4, 0, 5, 6, 7]
        case _:
            assert ibd_file_format in [
                "hapibd",
                "ilash",
                "germline",
                "rapid",
            ], f"The ibd format value provided, {ibd_file_format}, is not one of the allowed values ['hapibd', 'ilash', 'germline', 'rapid']"

    # because of our default check, the program will crash if the value is not one of our 4 cases
    return IbdFileIndices(*indices)  # pyright: ignore[reportPossiblyUnboundVariable]
