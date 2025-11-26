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


def create_indices(ibd_file_format: str) -> IbdFileIndices:
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
