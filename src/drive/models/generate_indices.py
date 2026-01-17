from collections import namedtuple

# Every value in this named tuple will be a string because the column names are strings
IbdFileIndices = namedtuple(
    "IbdFileIndices",
    [
        "prog_name",
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
    """Factory method to generate the proper file index object based on the ibd program

    Parameters
    ----------
    ibd_file_format: str
        string indicating what ibd program was used identify IBD segments. EX: hapibd,
        ilash, rapid, and germline. expects this value to be lower case

    Returns
    -------
    IbdFileIndices
        returns a named tuple with the appropriate indices for each column of interest in the file
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
            indices = [
                "germline",
                "column0",
                "column1",
                "column2",
                "column3",
                "column4",
                "column5",
                "column6",
                "column10",
            ]
        case "hapibd":
            indices = [
                "hapibd",
                "column0",
                "column1",
                "column2",
                "column3",
                "column4",
                "column5",
                "column6",
                "column7",
            ]
        case "ilash":
            indices = [
                "ilash",
                "column0",
                "column1",
                "column2",
                "column3",
                "column4",
                "column5",
                "column6",
                "column9",
            ]
        case "rapid":
            indices = [
                "rapid",
                "column1",
                "column3",
                "column2",
                "column4",
                "column0",
                "column5",
                "column6",
                "column7",
            ]
        case _:
            assert ibd_file_format in [
                "hapibd",
                "ilash",
                "germline",
                "rapid",
            ], f"The ibd format value provided, {ibd_file_format}, is not one of the allowed values ['hapibd', 'ilash', 'germline', 'rapid']"

    # because of our default check, the program will crash if the value is not one of our 4 cases
    return IbdFileIndices(*indices)  # pyright: ignore[reportPossiblyUnboundVariable]
