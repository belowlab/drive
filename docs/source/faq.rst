DRIVE FAQ
=========

This section attempts to answer questions that people have commonly had or provide suggestions to common problems that people have identified.

.. dropdown:: What versions of Python is DRIVE compatible with?

    DRIVE supports Python versions >=3.9 except for Python 3.11.0 (Any other version of Python 3.11.* works fine). The allowed python version can always be found in the pyproject.toml file under the section "requires-python". 

    In the past, there was a bug that if you installed outside of the supported Python versions using either PYPI or Conda, then an old version of DRIVE would be installed and it would break the integration test. This bug is now rectified and, as long as you are within the aforementioned range, DRIVE should be able to be installed correctly. 

    You can check your python version using the command 'python --version'. If your system python version is outside of the allowed range then you can either install an appropriate version from `Python.org <https://www.python.org/downloads/>`_ or a package manager such as Homebrew on MacOS `Homebrew <https://brew.sh/>`_, or `Conda <https://anaconda.org/anaconda/conda>`_ where you can specify the python version. *Additionally*, DRIVE does not support the multithreaded version of python that allows users to disable the GIL since there are still packages that not yet compatible with this experimental version of python. You can check to see if this version is installed by running 'python --version'. If the result is python3.13t or python3.13t-dev then this is the incorrect version.


.. dropdown:: What are the main differences between DRIVE v1 and DRIVE v3?

    There are a handful of differences and improvements that were added to DRIVE v3 that make it distinct from version 1.0:

    * **Addition of phenotype enrichment test**

      The original implementation of DRIVE only perform network clustering. DRIVE v3 added a phenotypic enrichment test that the user can enable by providing a case/control file. This enrichment test using binomial statistics to test if a network is enriched for cases compared to the total cohort. This test will be performed for all networks that have 2 or more cases. Users can customize this test with their own code using the plugin architecture of DRIVE. This new test is also generalized so that users can provide a file with case/control definitions for multiple phecodes. This generalization allows users to run a PheWES (Phenomewide Enrichment Study) using a phenotype file format similar to whats required by many PheWAS tools.

    * **Extensibility through the plugins**

      DRIVE v3 is designed to interface with existing analytical pipelines through an flexible and extensible backend. This backend relies on the plugin architecture described in more detail here :doc:`Plugin Description </plugin_descriptions/plugin_architecture>`. Users can create their own "plugins" to perform additional analyses or output data in a more convenient format. This flexibility allows users to adjust DRIVE to their use cases without having to wait for formal updates to DRIVE from the Belowlab. You can click on this links to read more information about the way DRIVE stores the network data in the :doc:`Data API </plugin_descriptions/data_container_api>` or to view an example of a valid plugin :doc:`plugin template </plugin_descriptions/expected_plugin_structure>`

    * **Performance increases**

      In designing DRIVE v3, we took advantage of features of common data science libraries such as Pandas and PyArrow to boost performance. Current profiling shows a 10 fold improvement when running only the clustering algorithm over the CFTR locus in pairwise IBD segments for 250,000 individuals. The increase in memory comes from reading the data in in large chunks of dataframes rather than reading the file line by line. Since DRIVE was designed to be used primarily on servers or the cloud we figured this to be an acceptable increase (although you can control the size of chunks being read in using the chunksize argument.)

      .. list-table:: DRIVE v1 performance compared to DRIVE v3
          :widths: 25 50 25
          :header-rows: 1

          * - DRIVE version
            - Runtime
            - Memory
          * - v1
            - 37 hours and 14 minutes
            - 3 Gb
          * - v3
            - 1 hour and 38 minutes
            - 32 Gb

    * **Improved logging and error handling**

      DRIVE v1 did not utilize any logging and often let the program tactlessly crash when it encountered errors. Now DRIVE has more robust error handling and logging functionality that the user can customize through a verbosity flag "-v". There are almost certainly still ways to get the program to crash, but we have attempt to cover many of the errors commonly encountered in development. If you encounter new errors that you think are worth handling please let us know by submitting a github issue so we can reproduce the error and then determine the best way to implement error handling.

    * **Incorporation of the ability to generate dendrograms into the DRIVE codebase**

      In the original publication using DRIVE v1, the dendrogram of a network of interest was visualized using the phylogenetic tree generator `ATGC: FastME <http://www.atgc-montpellier.fr/fastme/>`_. This approach required the user to rely on a second software tool not maintained by the Belowlab. For DRIVE v3, we implemented our own dendrogram generation using scipy and packaged it in a DRIVE subcommand called dendrogram. This approach allows us to ensure that the dendrogram functionality stays consistent and is optimized to work with the DRIVE output without requiring the user to perform a lot of post-processing.

.. dropdown:: Not familar with Object-Oriented Programming so how do I design a plugin?

      DRIVE relies very heavily on the object-oriented programming (OOP) paradigm to implement the plugin architecture. We are not expecting every one to be an expert in OOP to design their own plugins. For that reason we have provided a template of the plugin structure :doc:`here </plugin_descriptions/expected_plugin_structure>`. The user can add their code in the analyze function. The user will also have to give the plugin a name in the name field right above the analyze function and they will have to python file name (without the .py suffix) in the quoted section of the initialize function.
