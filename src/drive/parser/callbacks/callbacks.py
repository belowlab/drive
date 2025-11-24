import argparse
from os import name
import sys
from pathlib import Path


class CheckInputExist(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs) -> None:
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(CheckInputExist, self).__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Path,
        option_string: str = None,
    ) -> None:
        if values.exists():
            setattr(namespace, self.dest, values)
        else:
            print(
                f"ERROR: The file, {values}, was not found. Please make sure that there is not a typo in the file name."
            )
            sys.exit(1)


class CheckPvalRange(argparse.Action):
    """a pval can only be between 0-1 so we are checking to make sure that
    this value falls in the appropriate range"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs) -> None:
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(CheckPvalRange, self).__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.ArgumentParser,
        values: float,
        option_string: str = None,
    ) -> None:
        if 0 <= values <= 1:
            setattr(namespace, self.dest, values)
        else:
            print(
                "ERROR: The p-value threshold has to be in the range [0,1]. Please make sure that your threshold falls within this range"
            )
            sys.exit(1)
