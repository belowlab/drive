.. DRIVE documentation master file, created by

   sphinx-quickstart on Sat May  6 10:53:12 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DRIVE's documentation!
=================================

Distant Relatedness for Identification and Variant Evaluation (DRIVE) is a novel approach to IBD-based genotype inference used to identify shared chromosomal segments in dense genetic arrays. DRIVE implemented a random walk algorithm that identifies clusters of individuals who pairwise share an IBD segment overlapping a locus of interest. This tool was developed in python by the Below Lab at Vanderbilt University.

Quick Installation:
-------------------
The easiest way to install DRIVE is from the PYPI register. Users can use the following command to install the program. This method ensures that all the necessary dependencies are installed. To read more about this install method go to the :doc:`Pip Installation <installation/pip_installation>`

.. code:: bash

   pip install drive-ibd

.. important:: 

   DRIVE supports Python versions >=3.9 and not 3.11.0 (other versions of 3.11 work fine) for compatibility between packages. It is expected that your python version falls within this range when attempting to install the software. You can check the python version using the 'python --version' command. If the version number is outside of the acceptable range then you must install an appropriate version from sources such as `Python.org <https://www.python.org/downloads/>`_, or a package manager such as `Homebrew <https://brew.sh/>`_ on MacOS, `Conda <https://anaconda.org/anaconda/conda>`_, or the appropriate Linux package manage if you are running Linux. *Additionally*, DRIVE doesn't support the development version of python 3.13t that allows users to disable the GIL due to some packages not being fully compatible yet.

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
   /modules/modules



