from typer.testing import CliRunner
import pytest
import sys
import pandas as pd

sys.path.append("../IBDCluster")
from IBDCluster import app

runner = CliRunner()

# integration test using the raw cftr_and_vw_test_phecode_matrix.txt
# affected statuses
@pytest.mark.integtest
def test_sucessful_run_with_desc():
    result = runner.invoke(
        app,
        [
            "-o",
            "./",
            "-e",
            "./test.env",
            "-f",
            "./test_data/shared_segment_test_data_chr2.ibd.gz",
            "-c",
            "./test_data/cftr_and_vw_test_phecode_matrix.txt",
            "-g",
            "./test_data/gene_info.txt",
            "--cM",
            "5",
            "-l",
            "verbose",
            "-j",
            "./config.json",
            "-d",
            "./phecode_descriptions.txt",
        ],
    )

    assert result.exit_code == 0


# integration test using the raw cftr_and_vw_test_phecode_matrix.txt
# affected statuses
@pytest.mark.integtest
def test_sucessful_run_no_desc():
    result = runner.invoke(
        app,
        [
            "-o",
            "./",
            "-e",
            "./test.env",
            "-f",
            "./test_data/shared_segment_test_data_chr2.ibd.gz",
            "-c",
            "./test_data/cftr_and_vw_test_phecode_matrix.txt",
            "-g",
            "./test_data/gene_info.txt",
            "--cM",
            "5",
            "-l",
            "verbose",
            "-j",
            "./config.json",
        ],
    )

    assert result.exit_code == 0


@pytest.mark.integtest
def test_allpairs():
    """This test is going to check the output of the allpairs.txt file."""
    errors = []

    allpairs_df = pd.read_csv("./TEST_GENE/IBD_TEST_GENE_allpairs.txt", sep="\t")

    # first going to make sure there are the right number of columns
    if len(allpairs_df.columns) != 11:
        error = f"Expected the IBD_TEST_GENE_allpairs.txt file to have 11 columns. Instead there were {len(allpairs_df.columns)} columns"

        errors.append(error)

    # next checking to make sure the proper columns are identified
    col_list = [
        "program",
        "network_id",
        "pair_1",
        "pair_2",
        "phase_1",
        "phase_2",
        "chromosome",
        "gene_name",
        "start",
        "end",
        "length",
    ]

    dif_cols = [col for col in allpairs_df.columns if col not in col_list]

    if dif_cols:

        error = f"Expected the IBD_TEST_GENE_allpairs.txt file to have the columns {', '.join(col_list)}. Found different columns {', '.join(dif_cols)}"

        errors.append(error)

    # checking to make sure alll 17 networks were found
    if allpairs_df.network_id.max() != 17:

        error = f"Expected the allpairs.txt file to contain 17 unique network ids. Instead only {allpairs_df.network_id.max()} were found"

        errors.append(error)

    # checking the value of the network ids are the same for this person and that they were not assigned to multiple networks
    network_ids = list(
        set(
            allpairs_df[
                allpairs_df.phase_1 == "patient_id_100.2"
            ].network_id.values.tolist()
        )
    )

    if len(network_ids) != 1:
        error = f"expected the individual patient_id_100.2 to be in 1 network but instead the individual was found in networks {', '.join(network_ids)}"

        errors.append(error)

    if len(network_ids) == 1:

        network_id = network_ids[0]

        filtered_df = allpairs_df[allpairs_df.network_id == network_id]

        if filtered_df.shape[0] != 8:

            error = f"expected network {network_id} to have 8 connections. Instead found {filtered_df.shape[0]} connections"

            errors.append(error)

    # checking to make sure the 286.11_Pair_2_status is all zero like it should be
    # if not all(
    #     [val == 0 for val in allpairs_df["286.11_Pair_2_status"].values.tolist()]
    # ):

    #     error = f"expected all of the values in the 286.11_Pair_2_status column to be zero instead the values were {', '.join(allpairs_df['286.11_Pair_2_status'].value_counts().values.astype(str))}"

    #     errors.append(error)

    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))