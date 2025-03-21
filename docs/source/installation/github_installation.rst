Installing DRIVE from Github
============================
This installation method assumes that you are familiar with Git and Github, the commandline, and python's Anaconda package manager and that these programs are installed/can be install on whatever computing environment you are using. You will have to use all of these tools so you will need to be familiar enough with each one to run the example commands. If you wish to read the documentation for each of these then they will be listed below:

* **Git:** `Git Website <https://git-scm.com/>`_

* **Github:** `Github Website <https://github.com/>`_

* **Commandline Interface:** `This is probably overkill but here is a very indepth CLI tutorial <https://www.learnenough.com/command-line-tutorial>`_

* **Anaconda** `Anaconda Website <https://www.anaconda.com/>`_

.. admonition:: Optional Tip

    You can also use PDM to install the program. PDM is a python package manager (another alternative to Pip and Conda and all the other package manages) that has good dependency resolution to create a reproducible environment. You can read more about the project here [PDM documentation](https://pdm-project.org/en/latest/) and the steps to install it are described in the "Installation" section. For individuals wishing to contribute to DRIVE development, PDM is the current recommended way to install DRIVE. PDM allows for individuals to install all the necessary dependencies for both runtime and development so that code can be properly formatted and tested before it is committed. 

Steps to installing DRIVE:
--------------------------

Step 1: Clone the Github repository:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can clone the Github repository into your local environment using the command shown below:

.. code::

    git clone https://github.com/belowlab/drive.git


You should now have a directory called drive. You can check if this exists using the command:

.. code::

    ls drive/


The process should look similar to the screencasts below:

.. image:: /screencasts/github_cloning.gif
    :height: 300
    :align: center
    :alt: github cloning screencast


If you see a directory file tree then the program cloned correctly. If you receive an error saying that the directory does not exist, then you will have to debug the error to move onto step 2.

Step 2: Installing necessary dependencies:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*if not using PDM or are not interested in developing the project:* 

If you are not using PDM than you can directly clone the conda environment.yml file using the following command:

.. code::

    conda env create -f DRIVE_envi.yml

Make sure that you are in the drive directory. This command will create a virtual environment called DRIVE using python 3.6 with all the required dependencies. 

You can also just PIP to install the required dependencies from the pyproject.toml file. Make sure you are in the same direcotry as the pyproject.toml file and then run the following command:

.. code::
    
    pip install .

.. admonition:: Tip on pip installing

    If you are choosing to PIP install instead of conda it is recommend to create a virtualenv first. This environment can be created using the venv module from python.


*If using PDM:* 

PDM allows the user to install a specific version of python. The user can then create an environment using that python version and install dependencies. If PDM is being used to install dependencies then the user needs to first select a version of python ([see documentation for installing python with PDM](https://pdm-project.org/en/latest/usage/project/#install-python-interpreters-with-pdm)) and then create a virtual environment using PDM ([see PDM venv documentation](https://pdm-project.org/en/latest/usage/venv/)). Once these steps have completed then you can use PDM to install all dependencies.


.. warning::

    DRIVE has only been tested with python >= 3.6 and python <= 3.9. Other version of python may not work. For this reason it is currently recommended to specify the python version within this range.

Once you have created and activated the environment, you can install the necessary dependencies using the following command:

.. code::

    pdm install --with dev


.. image:: /screencasts/poetry_dependency_install.gif
    :height: 300
    :align: center
    :alt: screencast of installing dependencies using poetry


This command will install all of the runtime dependencies and not the developer dependencies. If you are developing the tool then you can use the command

.. code:: 
    
    pdm install 


*After Successful Install*
If successful you will have all the dependencies you need to run the program. You can check this by running the command:

.. code:: 

    python drive/drive.py -h


you should see the DRIVE cli as shown below: 

.. image:: /screencasts/drive_cli.gif
    :height: 300
    :align: center
    :alt: help message displayed by successful install of DRIVE