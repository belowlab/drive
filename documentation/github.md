---
layout: page
title: Github Installation
parent: Installation
grand_parent: Documentation
nav_order: 1
---
# Using Github to install IBDCluster:
---

This installation method assumes that you are familiar with Git and Github, the commandline, and python's Anaconda package manager and that these programs are installed/can be install on whatever computing environment you are using. You will have to use all of these tools so you will need to be familiar enough with each one to run the example commands. If you wish to read the documentation for each of these then they will be listed below:

* **Git:** [Git Website](https://git-scm.com/)

* **Github:** [Github Website](https://github.com/)

* **Commandline Interface:** [This is probably overkill but here is a very indepth CLI tutorial](https://www.learnenough.com/command-line-tutorial)

* **Anaconda** [Anaconda Website](https://www.anaconda.com/)

{: .optional }
***Optional Installation Dependency:*** <br> 
You can also use Poetry to install the program. Poetry is a python package manager (another alternative to Pip and Conda and all the other package manages) that has good dependency resolution to create a reproducible environment. You can read more about the project here [Poetry documentation](https://python-poetry.org/) and the steps to install it are described here [Poetry Installation](https://python-poetry.org/docs/#installation). Poetry is the current recommended way to install the program but it relies on you having the necessary privelleges to install the Poetry program into whatever system you are using. People trying to run this on a personal machine (probably unlikely) should have no difficultly installing Poetry but those running DRIVE on a server (Which considering its made for BioBank data will be most people) may run into permission errors. If you are running into permission errors than the documentation will indicate where your installation instructions are different.

## Steps to installing DRIVE:
The installation process can be broken into 4 steps. These are listed below and will be explained in further detail:

1. clone the Github repository to your local environment.
2. Installing necessary dependencies.
4. Add the program to you PATH so that you can call the program

## Step 1: Clone the Github repository:
You can clone the Github repository into your local environment using the command shown below:

```bash
git clone https://github.com/belowlab/drive.git
```

You should now have a directory called drive. You can check if this exists using the command:

```
ls drive/
```
If you see a directory file tree then the program cloned correctly. If you receive an error saying that the directory does not exist, then you will have to debug the error to move onto step 2.

## Step 2: Installing necessary dependencies:
*if not using Poetry:*
If you are not using Poetry than you can directly clone the conda environment.yml file using the following command:

```bash
conda env create -f DRIVE_envi.yml
```

Make sure that you are first in the drive directory. This command will create a virtual environment called DRIVE using python 3.6 with all the required dependencies.

*If using Poetry:*
If you are using poetry you will first have to create a new conda environment using the command below. You can replace the environment-name with whatever name you want to give the environment.

```bash
conda create -n <environment-name> python=3.6
```

{: .warning }
DRIVE has only been test with python >= 3.6 and python <= 3.8. Other version of python may not work. For this reason it is currently recommended to specify the python version as either 3.6 or 3.8 in the above command.

Once you have created and activated the environment, you can install the necessary dependencies using the following command:

```bash
poetry install --without dev
```

This command will install all of the runtime dependencies and not the developer dependencies. If you are developing the tool then you can use the command

```bash
poetry install --with dev
```


## Step 3: Add the program to you PATH so that you can call the program:
---
{: .optional }
Motivation for the 
This step is optional and is so that the user doesn't have to type the full file path to IBDCluster.py each time.


Once you install all of the 
