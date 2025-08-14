Installing DRIVE from Github
============================
This installation method assumes that you are familiar with Git, Github, the commandline, venv, and a python package manager (either PDM or the Anaconda package manager). It is also assumed that these programs are installed/can be install on whatever computing environment you are using. You will have to use all of these tools so you will need to be familiar enough with each one to run the example commands. If you wish to read the documentation for each of these then they will be listed below:

* .. card:: Git
    :link: https://git-scm.com/doc
    :shadow: sm
    
    Website for Git. This link specifically goes to the documentation site. There are videos that go over the basics as well as the online version of the "Pro Git" book that gives all the information you could ever want for Git

* .. card:: Github:
    :link: https://github.com/

    Github website documentation

* .. card:: Commandline Interface
    :link: https://www.learnenough.com/command-line-tutorial
    :shadow: sm

    This is probably overkill but here is a very indepth CLI tutorial

* .. card:: virtualenvs (specifically venv)
    :link: https://docs.python.org/3/library/venv.html
    :shadow: sm

    This is a common way to make virtual environments that is supported by the official python organization. This link describes venv and shows how to make a venv

* .. card:: Python Dependency Manager (PDM)
    :link: https://pdm-project.org/latest/
    :shadow: sm

    PDM is another package manager for python that aims to support the whole development process from initialization, package management, building, and deployment

* .. card:: Anaconda
    :link: https://www.anaconda.com/
    :shadow: sm

    Anaconda website that describes the installation and 


.. admonition:: For Developers

    For individuals wishing to contribute to DRIVE, PDM is the current recommended way to install DRIVE. PDM allows for individuals to install not only the necessary runtime dependencies but also the necessary development dependencies to properly format and commit the code so that they can follow the required standards while committing to the project. 

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
To install the necessary dependencies for DRIVE you have to use a python compatible package manager. For this documentation, we are going to assume you are using Conda, PDM, or PIP. There are other packages managers such as uv and Poetry which you are welcome to use but we make no guarantee that they can install DRIVE correctly. 

.. important:: 

   DRIVE supports Python versions >=3.9 and not 3.11.0 (other versions of 3.11 work fine) for compatibility between packages. It is expected that your python version falls within this range when attempting to install the software. You can read more about this version requirement and how to check if you have the right python version :doc:`here </faq>` under the dropdown section 'What versions of Python is DRIVE compatible with?'

**if not using PDM or are not interested in developing the project:**

If you are not using PDM than you can directly clone the conda environment.yml file using the following command:

.. code::

    conda env create -f DRIVE_envi.yml


Make sure that you are in the drive directory. This command will create a virtual environment called DRIVE using python 3.9 or newer with all the required dependencies. 

**If using PDM:**

PDM can install specific python versions `(documentation) <https://pdm-project.org/en/latest/usage/project/#install-python-interpreters-with-pdm>`_ and create virtual environments using a number of backends

.. warning::

    DRIVE has only been tested with python >= 3.9 and python <= 3.12. Other version of python may not work. For this reason it is currently recommended to specify the python version within this range.

Once you have created and activated the environment, you can install the necessary dependencies using the following command:

.. code::

    pdm install --without dev,docs

    or

    pdm install --prod

.. image:: /screencasts/pdm_installation.gif
    :height: 300
    :align: center
    :alt: screencast of installing dependencies using poetry


This command will install all of the runtime dependencies and not the developer dependencies. If you are developing the tool then you can use the command

.. code:: 
    
    pdm install --with dev

.. note::
    If you also want to work on the Documentation then you need to install the docs group with PDM.

**If using PIP**

Pip is able to install dependencies from the pyproject.toml file. It is recommended that you first create a python virtualenv (venv) using the appropriate python version and then use Pip to install dependencies into that venv. The following command will install all dependencies.

.. code::

    pip install .

**After Successful Install**

If successful you will have all the dependencies you need to run the program. You can check this by running the command:

.. code:: 

    python drive/drive.py -h


you should see the DRIVE cli as shown below: 

.. image:: /screencasts/drive_help_message.gif
    :height: 300
    :align: center
    :alt: help message displayed by successful install of DRIVE


You can additionally check to make sure you have the correct version of DRIVE using the following command. 

.. code::

    drive --version

The most up to date version of DRIVE can be found in the pyproject.toml file under the section "version". If your version is older than what is listed in the pyproject.toml than something went wrong during the install (Unless you purposefully installed an older version).
