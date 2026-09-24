import pytest
import drive.parser  # Ensure drive.parser initializes before drive.network to prevent circular import
from drive.network.network_algorithm import validate_provided_plugins


@pytest.fixture
def available_modules() -> list[dict[str, str]]:
    """Fixture providing simulated module definitions from config.json."""
    return [
        {"name": "pvalues", "description": "enrichment test"},
        {"name": "network_writer", "description": "writes output"},
        {"name": "summary_stats", "description": "additional plugin"},
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_input",
    [
        ["unknown_plugin"],
        ["pvalues", "unknown_plugin"],
        ["bad1", "bad2"],
    ],
)
def test_validate_plugins_raises_on_invalid_plugin(available_modules, bad_input):
    """Test that a ValueError is raised when any unknown plugin name is provided."""
    with pytest.raises(ValueError, match="Unknown plugin"):
        validate_provided_plugins(bad_input, available_modules)


@pytest.mark.unit
def test_validate_plugins_appends_network_writer_when_omitted(available_modules):
    """Test that network_writer is appended to the end if not specified by user."""
    result = validate_provided_plugins(["pvalues"], available_modules)
    names = [mod["name"] for mod in result]
    assert names == ["pvalues", "network_writer"]
    assert result[-1]["name"] == "network_writer"


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_plugins",
    [
        ["pvalues", "summary_stats", "network_writer"],
        ["network_writer", "pvalues", "summary_stats"],
        ["summary_stats", "network_writer", "pvalues"],
    ],
)
def test_validate_plugins_returns_multiple_with_writer_at_end(
    available_modules, input_plugins
):
    """Test that all specified plugins are returned and network_writer is always last."""
    result = validate_provided_plugins(input_plugins, available_modules)
    names = [mod["name"] for mod in result]

    assert set(names) == {"pvalues", "summary_stats", "network_writer"}
    assert names[-1] == "network_writer"


@pytest.mark.unit
def test_validate_plugins_default_none_returns_all(available_modules):
    """Test that requested_plugins=None returns all configured modules."""
    result = validate_provided_plugins(None, available_modules)
    assert len(result) == len(available_modules)


@pytest.mark.unit
def test_validate_plugins_deduplication_and_normalization(available_modules):
    """Test deduplication and comma-separated input handling."""
    # Deduplication test
    result_dedup = validate_provided_plugins(["pvalues", "pvalues"], available_modules)
    names_dedup = [mod["name"] for mod in result_dedup]
    assert names_dedup == ["pvalues", "network_writer"]

    # Comma-delimited input test
    result_comma = validate_provided_plugins(
        ["pvalues,summary_stats"], available_modules
    )
    names_comma = [mod["name"] for mod in result_comma]
    assert names_comma == ["pvalues", "summary_stats", "network_writer"]
