Installing DRIVE from Github
============================
This installation method assumes that you are familiar with Git, Github, the commandline, venv, and a python package manager (either PDM or the Anaconda package manager). It is also assumed that these programs are installed/can be install on whatever computing environment you are using. You will have to use all of these tools so you will need to be familiar enough with each one to run the example commands. If you wish to learn more about these tools then you can read the links below:

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

    Anaconda website that describes how to install Conda and how to use it


.. admonition:: For Developers

    For individuals wishing to contribute to DRIVE, PDM is the current required way to install DRIVE. PDM allows for individuals to install not only the necessary runtime dependencies but also the necessary development dependencies to format and commit the code so that they can follow the required standards while committing to the project. 

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


If you see a directory file tree then the program cloned correctly. If you receive an error saying that the directory does not exist, then you will have to debug the error to move onto step 2. All steps after this section assume that you have moved into the parent directory of the cloned github repository.

Step 2: Installing necessary dependencies:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To install the necessary dependencies for DRIVE you have to use a python compatible package manager. For this documentation, we are going to assume you are using Conda, PDM, or PIP. 

.. important:: 

   DRIVE supports Python versions >=3.10 (but not Python version 3.11.0 specifically) for compatibility between packages. It is expected that your python version falls within this range when attempting to install the software. You can read more about this version requirement and how to check if you have the right python version :doc:`here </faq>` under the dropdown section 'What versions of Python is DRIVE compatible with?'

.. tab-set::
   :sync-group: installation-types

   .. tab-item:: Conda
      :sync: key1 

      This installation is only recommanded for those not looking to contribute to DRIVE and those who do not prefer to directly install DRIVE using the :doc:`Pip installation method </installation/pip_installation>`. Everything described here would also work with `Mamba <https://mamba.readthedocs.io/en/latest/index.html>`_ (a faster version of conda) if you replace 'conda' with 'mamba'.

      Users can recreate an appropriate environment using the following command. The DRIVE_envi.yml file will be in the root directory of the cloned github repository.

      .. code::

         conda env create -f DRIVE_envi.yml


      Make sure that you are in the drive directory. This command will create a virtual environment called DRIVE using python 3.10 or newer with all the required dependencies. Once the environment is created, it can be activated using the following command:

      .. code::

        conda activate DRIVE


   .. tab-item:: PDM
      :sync: key2

      *This method is required if you are contributing to DRIVE development*

      **Using PDM to install Python:**
      PDM can install specific python versions `(documentation) <https://pdm-project.org/en/latest/usage/project/#install-python-interpreters-with-pdm>`_ and creates virtual environments using a number of backends. We recommend installing the newest stable version of python (currently 3.13) for development and using venv for the virtual environemnt backend. 

      Once you have installed the appropriate version of Python, then you can create a new virtual environment named drive-ibd and then instruct PDM to use this environment. The commands to do this are shown below:

      .. code::

        pdm venv create -n drive-ibd -w venv --force 3.13

        pdm use --venv drive-ibd
    
      
      Once you have created and activated the environment, PDM can then be used to install the necessary dependencies using the following commands:

      .. code::

          pdm install --without dev,docs

          or

          pdm install --prod

      .. image:: /screencasts/pdm_installation.gif
          :height: 300
          :align: center
          :alt: screencast of installing dependencies using PDM


      The above command will install all of the runtime dependencies and not the developer dependencies. If you are developing the tool then you can use the command

      .. code:: 
          
          pdm install --with dev,docs


   .. tab-item:: Pip
      :sync: key3

      **If using PIP**

      Pip is able to install dependencies from the pyproject.toml file. It is recommended that you first create a python virtualenv using the appropriate version of Python and then use Pip to install dependencies into that environment.. The following command will install all dependencies.

      .. code::

          pip install .


**After all the dependencies are installed:**

If successful you will have all the dependencies you need to run the program. You can check this by running the command:

.. code:: 

    python -m drive.drive --help

The above command runs DRIVE in module mode which is required to ensure that all packages are correctly imported in DRIVE.


Users should see the DRIVE cli as shown below: 

.. image:: /screencasts/drive_help_message.gif
    :height: 300
    :align: center
    :alt: help message displayed by successful install of DRIVE


You can additionally check to make sure you have the correct version of DRIVE using the following command. 

.. code::

    python -m drive.drive --version

The most up to date version of DRIVE can be found in the pyproject.toml file under the section "version". If your version is older than what is listed in the pyproject.toml than something went wrong during the install (Unless you purposefully installed an older version).

**Running test data:**

Users can also run DRIVE against the provided test data to ensure a successful installation using the following command:

.. code::

  python -m drive.drive utilities test

.. note::
  
  If you are contributing to DRIVE or you installed all of the dependencies using PDM then you should read the following section to run the test data: :doc:`testing for contributors </contributing/testing>`.


