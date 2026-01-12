import random
import string
from pathlib import Path


def generate_random_logfile_suffix(log_filename: str) -> str:
    """add a unique suffix to the end of the log filename if the
    log file already exist. This will prevent weird writing race
    conditions when multiple RIVE jobs are run in slurm using the
    default log filename

    Parameters
    ----------
    log_filename : str
        name of the log file (without the parent directory) that
        was passed by the user or the default value of DRIVE.log

    Returns
    -------
    str
        returns the new log filename with the suffix added
    """
    # Return an 8 character string of random letters and digits. 8 should be
    # enough that we don't have many collisions
    random_suffix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    prefix, suffix = log_filename.strip().split(".")

    return f"{prefix}_{random_suffix}.{suffix}"
