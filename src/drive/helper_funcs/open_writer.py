from contextlib import contextmanager
import gzip
from pathlib import Path
from typing import Generator, TextIO


@contextmanager
def open_writer(file_path: Path) -> Generator[TextIO, None, None]:
    """Context manager to open file for text writing, handling gzip compression.

    Parameters
    ----------
    file_path : Path
        Path to the destination file. If ending in .gz, it will be written
        with gzip compression using UTF-8 encoding.
    """
    if file_path.suffix == ".gz":
        with gzip.open(file_path, "wt", encoding="utf-8") as f:
            yield f
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            yield f
