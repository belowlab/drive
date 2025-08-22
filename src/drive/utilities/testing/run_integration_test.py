import argparse
import pytest
from pathlib import Path
import sysconfig
import sys

from log import CustomLogger

logger = CustomLogger.get_logger(__name__)


def run_integration_test(args: argparse.Namespace) -> None:
    logger.info("Running integration test to ensure that DRIVE was installed correctly")

    site_packages_path = Path(sysconfig.get_paths().get("platlib")) / "tests"

    if site_packages_path is None:
        logger.fatal(
            "Was not able to find the site-packages directory in the virtualenv that DRIVE was installed into. This error is unexpected. Please report this error to the maintainers. Terminating program..."
        )
        system_paths = ", ".join(sysconfig.get_paths())
        logger.debug(f"Current System paths are: {system_paths}")
        sys.exit(1)

    sys.path.append(site_packages_path)

    pytest.main(
        [
            "-v",
            site_packages_path / "test_integration.py",
            "-W",
            "ignore::DeprecationWarning",
        ]
    )
