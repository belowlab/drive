.. DRIVE documentation master file, created by

   sphinx-quickstart on Sat May  6 10:53:12 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DRIVE's documentation!
=================================

Distant Relatedness for Identification and Variant Evaluation (DRIVE) is a novel approach to IBD-based genotype inference used to identify shared chromosomal segments in dense genetic arrays. DRIVE implemented a random walk algorithm that identifies clusters of individuals who share a pairwise IBD segment overlapping a locus of interest. This tool was written in Python and developed by the Below Lab at Vanderbilt University.

Quick Installation:
-------------------
**Installing DRIVE:**
The easiest way to install DRIVE is from the PYPI register. Users can use the following command to install the program. This method ensures that all the necessary dependencies are installed. This method assumes you have either made a virtualenv (venv) or a conda environment to install the program into. To read more about this install method read the :doc:`Pip Installation <installation/pip_installation>` section.

.. code:: bash

   pip install drive-ibd

.. important:: 

   DRIVE supports Python versions >=3.10 (but not Python version 3.11.0) for compatibility between packages. It is expected that your python version falls within this range when attempting to install the software. You can check the python version using the 'python --version' command. If the version number is outside of the acceptable range then you must install an appropriate version from sources such as `Python.org <https://www.python.org/downloads/>`_, or a package manager such as `Homebrew <https://brew.sh/>`_ on MacOS, `Conda <https://anaconda.org/anaconda/conda>`_, or the appropriate Linux package manage if you are running Linux. *Additionally*, DRIVE doesn't support the development version of python 3.13t that allows users to disable the GIL due to some packages not being fully compatible yet.

**Check Version:**
Once you have installed DRIVE you should check the version to ensure that you have the most recent code. At the time of writing the newest version is 3.0.2 but you can also check the PYPI Badge at the top of the GitHub README.md. This badge will display the most recent version on PYPI. This check is important because the testing framework was not added to DRIVE until v3 so running the test with an older version of DRIVE will result in an error (see :doc:`FAQ </faq>`).

.. code:: bash

  drive --version


**Run test to check sucessful installation:**
Once you have ensured that the correct version is installed then you can run the integration test using the following command. 

.. code:: bash

  drive utilities test

These tests use simulated IBD data to check that DRIVE is identifying the correct networks and is creating the appropriate output files. You can read more about the simulations under the section called "Simulating IBD Data" :doc:`here </installation/testing>`

.. note::

   To read more about this install go to the Pip Installation section

Citation:
---------
The following paper discusses an initial implementation of the clustering algorithm of DRIVE (1.0.0) and can be citied if you use the tool: `Detection of distant relatedness in biobaks to identify undiagnosed cases of Mendelian disease as applied to Long QT Syndrome <https://doi-org.proxy.library.vanderbilt.edu/10.1038/s41467-024-51977-4>`_.


Contact:
--------
If you have any questions about DRIVE or run into issues, you can either post an issue on the Github issues page or you can contact us at the email address, insert email here.

.. toctree::
   :maxdepth: 2
   :caption: User's Guide
   :hidden:

   /about/about
   /installation/installation
   /inputs_and_outputs/inputs
   /inputs_and_outputs/outputs
   faq.rst
   
   

.. toctree::
   :maxdepth: 2
   :caption: Tutorial
   :hidden:

   /examples/examples_command_format

.. toctree::
   :maxdepth: 2
   :caption: Developer's Guide
   :hidden:

   /contributing/contributing
   /plugin_descriptions/extending_drive



