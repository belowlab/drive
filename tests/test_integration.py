
import pytest
import sys
import pandas as pd

sys.path.append("./src")

from drive import drive



# @pytest.mark.integtest
# def test_drive_full_run():
#     assert 1==1
@pytest.fixture()
def system_args(monkeypatch):
    monkeypatch.setattr("sys.argv", 
        [
            "drive", "-i",
            "./tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz",
            "-f",
            "hapibd",
            "-t",
            "20:4666882-4682236",
            "-o",
            "./tests/test_output/integration_test_results",
            "-m",
            "3",
            "--recluster"
            ])

@pytest.mark.integtest
def test_drive_full_run_no_phenotypes(system_args):
    drive.main()

    # result = runner.invoke(
    #     app,
    #     [
    #         "--help"
    #     ],
    #     color=True
    # )
    # we need to make sure the output was properly formed
    output = pd.read_csv("./tests/test_output/integration_test_results.drive_networks.txt", sep="\t")
    # list of errors to keep
    errors = []

    # list of columns it should have
    expected_colnames = ["clstID", "n.total", "n.haplotype", "true.positive.n", "true.positive", "falst.postive", "IDs", "ID.haplotype"]

    if not output.shape == (165, 8):
        errors.append(f"Expected the output to have 165 rows and 8 columns instead it had {output.shape[0]} rows and {output.shape[1]}")
    if [col for col in output.columns if col not in expected_colnames]:
        errors.append(f"Expected the output to have the columns: {','.join(expected_colnames)}, instead these columns were found: {','.join(output.columns)}")
        
    assert not errors, "errors occured:\n{}".format("\n".join(errors))
