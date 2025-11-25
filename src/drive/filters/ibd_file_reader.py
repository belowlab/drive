from pandas import DataFrame


def add_haplotype_id(
    data: DataFrame,
    ind_id_indx: int,
    phase_col_indx: int,
    col_name: str,
    ibd_file_format: str,
) -> None:
    """function to add the haplotype id to the dataframe"""
    match ibd_file_format:
        case "hapibd" | "rapid":
            data.loc[:, col_name] = (
                data[ind_id_indx] + "." + data[phase_col_indx].astype(str)
            )
        case "germline" | "ilash":
            data.loc[:, col_name] = data[phase_col_indx]
        case _:
            assert ibd_file_format in [
                "hapibd",
                "ilash",
                "germline",
                "rapid",
            ], f"The ibd format value provided, {ibd_file_format}, is not one of the allowed values ['hapibd', 'ilash', 'germline', 'rapid']"
