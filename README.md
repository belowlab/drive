[![Documentation Status](https://readthedocs.org/projects/drive-ibd/badge/?version=latest)](https://drive-ibd.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/drive-ibd.svg)](https://badge.fury.io/py/drive-ibd)
[![DRIVE python package](https://github.com/belowlab/drive/actions/workflows/python-app.yml/badge.svg)](https://github.com/belowlab/drive/actions/workflows/python-app.yml)

# DRIVE

This repository contains the source code for the tool DRIVE (Distant Relatedness for Identification and Variant Evaluation) is a novel approach to IBD-based genotype inference used to identify shared chromosomal segments in dense genetic arrays. DRIVE implements a random walk algorithm that identifies clusters of individuals who pairwise share an IBD segment overlapping a locus of interest. This tool was developed in Python by the Below Lab at Vanderbilt University. The documentation for how to use this tool can be found here [DRIVE documentation](https://drive-ibd.readthedocs.io/en/latest/)

## Installing DRIVE

**Python Versions**:
DRIVE supports Python versions >=3.9 && and not 3.11.0 (Any other version of Python 3.11.* works fine). The allowed python version can always be found in the pyproject.toml file under the section "requires-python". In the past, there was a bug that if you installed outside of the supported Python versions using either PYPI or Conda, then an old version of DRIVE would be installed and it would break the integration test. This bug is now rectified and, as long as you are within the aforementioned range, DRIVE should be able to be installed correctly. You can check your python version using the command 'python --version'. If your system python version is outside of the allowed range then you can either install an appropriate version from [Python.org](https://www.python.org/downloads/) or a package manager such as Homebrew on MacOS [Homebrew](https://brew.sh/), or [Conda](https://anaconda.org/anaconda/conda) where you can specify the python version. *Additionally*, DRIVE does not support the multithreaded version of python that allows users to disable the GIL since there are still packages that not yet compatible with this experimental version of python. You can check to see if this version is installed by running 'python --version'. If the result is python3.13t or python3.13t-dev then this is the incorrect version.

**Checking the installed version**:
After installing DRIVE You can check what version was installed to see if it is up to date using the following command (Assuming that you have activated the environment into which you installed DRIVE):

```bash
drive --version
```

You should see v3.0.2 (The project version is always listed in the pyproject.toml under the section "version" as well). If the version is older than 3.0 then something went wrong with the install (unless you did intentionally installed an old version). Older versions of DRIVE before 3.0.0 will break the integration test because the command structure of the CLI was different. If you still wish to run the test with an older version then look at the section of the documentation call "testing legacy versions" #TODO: make this page in the documentation

**PYPI Installation:**
DRIVE is available on PYPI and can easily be installed using the following command:

```bash
pip install drive-ibd
```

It is recommended to install DRIVE within a virtual environment such as venv, or conda. More information about this process can be found within the documentation.

**Github Installation/Installing from source**
If the user wishes to develop DRIVE or install the program from source then they can clone the repository. This process is described under the section called "Github Installation" in the documentation.

**Docker Installation**
DRIVE is also available on Docker. The docker image can be found here [jtb114/drive](https://hub.docker.com/r/jtb114/drive). The command to pull the image can be found on that page.

If you are working on an HPC cluster it may be better to use a singularity image. Singularity can pull the docker container and build a singularity image with the following command:

```bash
singularity pull singularity-image-name.sif docker://jtb114/drive:latest
```

### Reporting issues

If you wish to report a bug or propose a feature you can find templates under the .github/ISSUE_TEMPLATE directory.
