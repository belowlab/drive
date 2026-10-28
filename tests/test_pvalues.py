from pathlib import Path

import numpy as np
import pytest
from scipy.stats import mannwhitneyu

import drive.parser  # Ensure drive.parser initializes before drive.network to prevent circular import
from drive.network.models.data_container import RuntimeState
from drive.network.models.networks import Network
from drive.parser.phenotype_descriptions_parser import PhecodesMapper
from drive.plugins.pvalues import Pvalues


@pytest.fixture
def sample_network() -> Network:
    """Fixture providing a mock network for testing."""
    return Network(
        clst_id=1.0,
        true_positive_count=2,
        true_positive_percent=1.0,
        false_negative_edges=[],
        false_negative_count=0,
        members={"ID1", "ID2", "ID3", "ID4"},
        haplotypes=["ID1_A", "ID2_A", "ID3_A", "ID4_A"],
    )


@pytest.mark.unit
def test_determine_pvalue_continuous_valid_distribution() -> None:
    """Test Mann-Whitney U calculation against scipy with valid distributions."""
    network_values = [15.2, 14.8, 16.1, 15.5]
    cohort_values = [2.1, 1.9, 2.5, 3.0, 1.8]

    pvalue = Pvalues._determine_pvalue_continuous(
        network_values, cohort_values, alternative="two-sided"
    )

    expected = mannwhitneyu(
        network_values, cohort_values, alternative="two-sided"
    ).pvalue
    assert isinstance(pvalue, np.float64)
    assert np.isclose(pvalue, expected)
    assert pvalue < 0.05


@pytest.mark.unit
def test_determine_pvalue_continuous_insufficient_samples() -> None:
    """Test that sample sizes < 2 in either group return 1.0 safely."""
    # Network empty
    assert Pvalues._determine_pvalue_continuous([], [1.0, 2.0, 3.0]) == 1.0

    # Network has 1 observation
    assert Pvalues._determine_pvalue_continuous([5.0], [1.0, 2.0, 3.0]) == 1.0

    # Cohort empty
    assert Pvalues._determine_pvalue_continuous([1.0, 2.0, 3.0], []) == 1.0

    # Cohort has 1 observation
    assert Pvalues._determine_pvalue_continuous([1.0, 2.0, 3.0], [5.0]) == 1.0


@pytest.mark.unit
def test_determine_pvalue_continuous_zero_variance_identical_values() -> None:
    """Test that identical values across samples safely return 1.0 and log context."""
    network = [5.0, 5.0, 5.0]
    cohort = [5.0, 5.0, 5.0]

    pvalue = Pvalues._determine_pvalue_continuous(
        network, cohort, network_id=1, phenotype="TraitA"
    )
    assert pvalue == 1.0


@pytest.mark.unit
def test_determine_pvalue_continuous_alternative_hypotheses() -> None:
    """Test directional alternative hypotheses for the Mann-Whitney test."""
    network = [10.0, 11.0, 12.0, 13.0]
    cohort = [1.0, 2.0, 3.0, 4.0]

    p_greater = Pvalues._determine_pvalue_continuous(
        network, cohort, alternative="greater"
    )
    p_less = Pvalues._determine_pvalue_continuous(network, cohort, alternative="less")

    assert p_greater < 0.05
    assert p_less > 0.95


@pytest.mark.unit
def test_gather_continuous_partitioning_and_exclusion(
    sample_network: Network,
) -> None:
    """Test sample partitioning, exclusion tracking, and output format for continuous traits."""
    plugin = Pvalues()
    # sample_network.members = {"ID1", "ID2", "ID3", "ID4"}
    cohort_phenotypes = {
        "Trait1": {
            "values": {"ID1": 10.0, "ID2": 12.0, "ID5": 2.0, "ID6": 3.0},
            "excluded": {"ID3", "ID7"},
        }
    }

    min_pval, min_pheno, pheno_pvals = plugin._gather_network_information_continuous(
        sample_network, cohort_phenotypes
    )

    assert min_pheno == "Trait1"
    assert min_pval != "N/A"

    trait1_str = pheno_pvals["Trait1"]
    parts = trait1_str.split("\t")
    assert len(parts) == 5

    # 1. Case count string must be "N/A"
    assert parts[0] == "N/A"
    # 2. Cases string must be "N/A"
    assert parts[1] == "N/A"
    # 3. Excluded count in network (ID3)
    assert parts[2] == "1"
    # 4. Exclusion string
    assert parts[3] == "ID3"
    # 5. P-value matches scipy calculation
    expected_p = mannwhitneyu([10.0, 12.0], [2.0, 3.0], alternative="two-sided").pvalue
    assert np.isclose(float(parts[4]), expected_p)


@pytest.mark.unit
def test_gather_continuous_multiple_phenotypes_min_pvalue(
    sample_network: Network,
) -> None:
    """Test identifying the minimum p-value among multiple continuous phenotypes."""
    plugin = Pvalues()
    cohort_phenotypes = {
        "EnrichedTrait": {
            "values": {"ID1": 100.0, "ID2": 102.0, "ID5": 1.0, "ID6": 2.0},
            "excluded": set(),
        },
        "NonEnrichedTrait": {
            "values": {"ID1": 1.0, "ID2": 2.0, "ID5": 1.0, "ID6": 2.0},
            "excluded": set(),
        },
    }

    min_pval, min_pheno, pheno_pvals = plugin._gather_network_information_continuous(
        sample_network, cohort_phenotypes
    )

    assert min_pheno == "EnrichedTrait"
    assert float(min_pval) < float(pheno_pvals["NonEnrichedTrait"].split("\t")[4])
    assert "EnrichedTrait" in pheno_pvals
    assert "NonEnrichedTrait" in pheno_pvals


@pytest.mark.unit
def test_gather_continuous_empty_network_measurements(
    sample_network: Network,
) -> None:
    """Test network gathering when no network members have measurements."""
    plugin = Pvalues()
    # No network members present in values
    cohort_phenotypes = {
        "TraitMissing": {
            "values": {"ID5": 1.0, "ID6": 2.0},
            "excluded": set(),
        }
    }

    min_pval, min_pheno, pheno_pvals = plugin._gather_network_information_continuous(
        sample_network, cohort_phenotypes
    )

    parts = pheno_pvals["TraitMissing"].split("\t")
    assert parts[0] == "N/A"  # case count string is N/A
    assert parts[1] == "N/A"  # cases string is N/A
    assert parts[2] == "0"  # 0 excluded in network
    assert parts[3] == "N/A"
    assert parts[4] == "1.0"


@pytest.mark.unit
def test_analyze_branches_to_continuous_when_flag_set(
    sample_network: Network,
) -> None:
    """Test that analyze() runs the continuous pipeline when run_continuous_trait is True."""
    cohort_phenotypes = {
        "Trait1": {
            "values": {"ID1": 10.0, "ID2": 12.0, "ID5": 1.0, "ID6": 2.0},
            "excluded": set(),
        }
    }
    desc_mapper = PhecodesMapper(phecode_names={"Trait1": "Continuous Test Trait"})

    state = RuntimeState(
        networks=[sample_network],
        output_path=Path("."),
        carriers=cohort_phenotypes,
        phenotype_descriptions=desc_mapper,
        config_options={"run_continuous_trait": True},
    )

    plugin = Pvalues()
    plugin.analyze(data=state)

    assert hasattr(sample_network, "min_pvalue_str")
    assert "Trait1" in sample_network.min_pvalue_str
    assert "Continuous Test Trait" in sample_network.min_pvalue_str

    parts = sample_network.pvalues["Trait1"].split("\t")
    assert parts[0] == "N/A"  # Case count string is N/A
    assert parts[1] == "N/A"  # Cases string is N/A


@pytest.mark.unit
def test_analyze_branches_to_binary_when_flag_false(
    sample_network: Network,
) -> None:
    """Test that analyze() defaults to binary binomial test when run_continuous_trait is False."""
    binary_carriers = {
        "Phe1": {
            "cases": {"ID1", "ID2", "ID3", "ID4"},
            "controls": {f"CTRL_{i}" for i in range(100)},
            "excluded": set(),
        }
    }
    desc_mapper = PhecodesMapper(phecode_names={"Phe1": "Binary Test Phecode"})

    state = RuntimeState(
        networks=[sample_network],
        output_path=Path("."),
        carriers=binary_carriers,
        phenotype_descriptions=desc_mapper,
        config_options={"run_continuous_trait": False},
    )

    plugin = Pvalues()
    plugin.analyze(data=state)

    assert hasattr(sample_network, "min_pvalue_str")
    assert "Phe1" in sample_network.min_pvalue_str

    parts = sample_network.pvalues["Phe1"].split("\t")
    # In binary, parts[1] contains case IDs (e.g., 'ID1, ID2' or 'ID2, ID1')
    assert parts[1] != "N/A"
    assert "ID1" in parts[1] or "ID2" in parts[1]


@pytest.mark.unit
def test_analyze_handles_empty_carriers(sample_network: Network) -> None:
    """Test that analyze() gracefully handles empty carriers dictionary."""
    state = RuntimeState(
        networks=[sample_network],
        output_path=Path("."),
        carriers={},
        phenotype_descriptions=PhecodesMapper(),
    )

    plugin = Pvalues()
    plugin.analyze(data=state)
    assert not hasattr(sample_network, "pvalues") or sample_network.pvalues == {}
