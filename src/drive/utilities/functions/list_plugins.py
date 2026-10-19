from pathlib import Path
from argparse import Namespace
import json
from rich.console import Console
from rich.table import Table
from rich import box


def find_json_file() -> Path | None:
    """Method to find the default config file if the user does not provide one

    Returns
    -------
    Path | None
        returns the path to the json file. Returns None if the configuration
        path doesn't exist

    """

    src_dir = Path(__file__).parent.parent.parent

    config_path = src_dir / "config.json"

    if not config_path.exists():
        return None

    return config_path


def list_plugins(args: Namespace) -> None:
    """list the plugins that the user can access based on the current
    configuration file

    Parameters
    ----------
    args : Namespace
        The namespace that all the user parameters are read into at the
        start of the programs runtime

    Raises
    ------
    AssertionError
        raises an AssertionError if the json configuration file can't be
        discovered
    """
    # initialize the console class from rich that we will use for
    # formatting text
    console = Console()

    # Make sure the configuration file can be discovered at runtime
    json_config = args.json_config if args.json_config else find_json_file()

    # We will use the rich console to make the error message more
    # colorful by default
    try:
        assert (
            json_config is not None
        ), "No configuration file was detected for DRIVE. This means that the user didn't provide a value and that the configuration file packaged with DRIVE has been deleted. Please re-download this file from the Github"
    except AssertionError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

    # We will use a rich table to display the plugins
    table = Table(title="Detected Plugins:", box=box.MINIMAL, padding=(1, 2))
    table.add_column("Name", justify="center", style="dark_orange3")
    table.add_column("Description", justify="left", style="bright_white", no_wrap=False)

    with open(
        json_config, encoding="utf-8"  # pyright: ignore[reportArgumentType]
    ) as json_config:
        config = json.load(json_config)

        for plugin in config["modules"]:
            table.add_row(plugin["name"], plugin["description"])

    console.print(table)
