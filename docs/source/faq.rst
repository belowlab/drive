DRIVE FAQ
=========

This section addresses frequently asked questions and provides solutions to common problems identified by users.

.. dropdown:: What versions of Python is DRIVE compatible with?

    DRIVE supports Python versions >=3.10 (but not Python version 3.11.0 specifically). The allowed Python version can always be found in the pyproject.toml file under the section "requires-python". 

    In the past, there was a bug where installing outside of the supported Python versions using either PyPI or Conda would cause an old version of DRIVE to be installed, breaking the integration tests. This bug is now rectified and, as long as you are within the aforementioned range, DRIVE should install correctly. 

    You can check your Python version using the command 'python --version'. If your system Python version is outside of the allowed range, you can either install an appropriate version from `Python.org <https://www.python.org/downloads/>`_, a package manager such as `Homebrew <https://brew.sh/>`_ on MacOS, or `Conda <https://anaconda.org/anaconda/conda>`_ where you can specify the Python version. *Additionally*, DRIVE does not support the multithreaded version of Python that allows users to disable the GIL, as there are still packages that are not yet compatible with this experimental version of Python. You can check to see if this version is installed by running 'python --version'. If the result is python3.13t or python3.13t-dev, then this is the incorrect version.

.. dropdown:: Why is there no v2? 

    DRIVE v2 was a purely internal implementation of DRIVE. When the plugin architecture was added to DRIVE, we considered this a major change to the user interface which prompted us to change from v1 to v2 based on semantic versioning practic cases. Over the past year, the scope of DRIVE changed again to add the dendrogram functionality through a new subcommand structure (similar to git). This subcommand structure represented another significant change to the user interface, which prompted us to update the version to v3 before publication.


.. dropdown:: What are the main differences between DRIVE v1 and DRIVE v3?

    There are a handful of differences and improvements added to DRIVE v3 that make it distinct from version 1.0:

    * **Addition of phenotype enrichment test**

      The original implementation of DRIVE only performed network clustering. DRIVE v3 added a phenotypic enrichment test that users can enable by providing a case/control file. This enrichment test uses binomial statistics to determine if a network is enriched for cases compared to the total cohort. This test will be performed for all networks that have 2 or more cases. Users can customize this test with their own code using the plugin architecture of DRIVE. This new test is also generalized so that users can provide a file with case/control definitions for multiple phecodes. This generalization allows users to run a PheWES (Phenome-wide Enrichment Study) using a phenotype file format similar to what is required by many PheWAS tools.

    * **Extensibility through plugins**

      DRIVE v3 is designed to interface with existing analytical pipelines through a flexible and extensible backend. This backend relies on the plugin architecture described in more detail here: :doc:`Plugin Description </plugin_descriptions/plugin_architecture>`. Users can create their own "plugins" to perform additional analyses or output data in a more convenient format. This flexibility allows users to adjust DRIVE to their use cases without having to wait for formal updates to DRIVE from the Below Lab. You can click on this link to read more information about the way DRIVE stores the network data in the :doc:`Data API </plugin_descriptions/data_container_api>` or to view an example of a valid plugin: :doc:`plugin template </plugin_descriptions/expected_plugin_structure>`

    * **Performance increases**

      In designing DRIVE v3, we took advantage of features of common data science libraries such as Pandas, PyArrow, and DuckDB to boost performance. Current profiling shows a ~35x improvement when running only the clustering algorithm over the CFTR locus in pairwise IBD segments for 250,000 individuals. The performance increase resulted in moving the IBD segment I/O and filtering to DuckDB. In v1, DRIVE read this data in 1 line at a time and appended the new line to a (growing) pandas dataframe. This process resulted in many memory allocations, which became slower as the dataframe grew in size. DuckDB enables DRIVE to use multiple threads to read in and filter the file. With the inclusion of DuckDB, this step of DRIVE is now multi-threaded but the rest of the runtime which relies on pandas, iGraph, and scipy is still single threaded.

      .. list-table:: DRIVE v1 performance compared to DRIVE v3
          :widths: 25 25 25 25
          :header-rows: 1

          * - DRIVE version
            - Runtime (Wall Clock)
            - Runtime (User Time)
            - Memory Consumption
          * - v1
            - 36h 16m
            - 20h 25m
            - 3.1 Gb
          * - v3
            - 1h 3m
            - 1h 11m
            - 7.1 Gb

    * **Improved logging and error handling**

      DRIVE v1 did not utilize any logging and often let the program tactlessly crash when it encountered errors. Now DRIVE has more robust error handling and logging functionality that the user can customize through a verbosity flag "-v". There are almost certainly still ways to get the program to crash, but we have attempted to cover many of the errors commonly encountered in development. If you encounter new errors that you think are worth handling please let us know by submitting a GitHub issue so we can reproduce the error and then determine the best way to implement error handling.

    * **Incorporation of the ability to generate dendrograms into the DRIVE codebase**

      In the original publication using DRIVE v1, the dendrogram of a network of interest was visualized using the phylogenetic tree generator `ATGC: FastME <http://www.atgc-montpellier.fr/fastme/>`_. This approach required the user to rely on a second software tool not maintained by the Below Lab. For DRIVE v3, we implemented our own dendrogram generation using scipy and packaged it in a DRIVE subcommand called dendrogram. This approach allows us to ensure that the dendrogram functionality stays consistent and is optimized to work with the DRIVE output without requiring the user to perform a lot of post-processing.
      In the original publication using DRIVE v1, the dendrogram of a network of interest was visualized using the phylogenetic tree generator `ATGC: FastME <http://www.atgc-montpellier.fr/fastme/>`_. This approach required the user to rely on a second software tool not maintained by the Below Lab. For DRIVE v3, we implemented our own dendrogram generation using scipy and packaged it in a DRIVE subcommand called dendrogram. This approach allows us to ensure that the dendrogram functionality stays consistent and is optimized to work with the DRIVE output without requiring the user to perform a lot of post-processing.

.. dropdown:: Not familiar with Object-Oriented Programming so how do I design a plugin?

      DRIVE relies very heavily on the object-oriented programming (OOP) paradigm to implement the plugin architecture. We are not expecting everyone to be an expert in OOP to design their own plugins. For that reason we have provided a template of the plugin structure :doc:`here </plugin_descriptions/expected_plugin_structure>`. The user can add their code in the analyze function. The user will also have to give the plugin a name in the name field right above the analyze function and they will have to provide a python file name (without the .py suffix) in the quoted section of the initialize function.


.. dropdown:: How was the test data generated? 

      The simulated IBD segments used as input for DRIVE were generated using a similar procedure as described in Tang et al: `Open-source benchmarking of IBD segment detection methods for biobank-scale cohorts <https://doi.org/10.1093/gigascience/giac111>`_. You can read a detailed description of how we generated the testing data under the section called :doc:`Simulating IBD Data: </installation/testing>`.

.. dropdown:: How can I report any issues that I find with DRIVE?

      To keep track of issues with DRIVE we ask that you open a GitHub issue. We have provided a template that can be found at ".github/ISSUE_TEMPLATE" within the repository. We ask that you use this format because it helps us to understand your issue and to reproduce it.
