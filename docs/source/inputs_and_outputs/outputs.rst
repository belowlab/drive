DRIVE Output
============

DRIVE cluster command outputs:
------------------------------

The cluster subcommand currently outputs two files. These files are described below.

*Networks File*
```````````````
DRIVE creates a file with the suffix ".drive_networks.txt". This file has the results from the clustering analysis with information such as number of members, members' IDs, haplotype IDs, how connected the graph is internally, and the binomial test statistics. This file has at a minimum of 11 columns depending on whether the user provides a phenotype file or not. These columns, plus the possible additional columns are described below.

Column descriptions:
^^^^^^^^^^^^^^^^^^^^

* **clstID**: ID given to each network identified. This value will have the form "clst#".

----

* **n.total**: Total number of individuals in the network.

----

* **n.haplotype**: The number of haplotypes in the network. This value may be different than n.total due to inbreeding.

----

* **true.positive.n**: Number of shared IBD segments that are identified in the network. 

----

* **true.positive**: Proportion of identified IBD segments in networks vs the total number of possible IBD segments that could exist between all individuals in the network.

----

* **false.positive**: Proportion of individuals within the cluster that share an IBD segment with another individual outside of the cluster.

----

* **IDs**: List of IDs that are in the network. 

----

* **ID.haplotype**: List of haplotypes that are in the network. These will be equivalent to the IDs in the "IDs" column except each ID will have a phase value attached to it.

----

* **min_pvalue**: Value of the smallest p-value calculated for the network from the binomial test. If a phenotype file is not provided then this value will be N/A.
* **min_pvalue**: Value of the smallest p-value calculated for the network from the binomial test. If a phenotype file is not provided then this value will be N/A.

----

* **min_phenotype**: Name of the phenotype that corresponds to the smallest p-value. This value will also be N/A if a phenotype file is not provided.

----

* **min_phenotype_description**: Description of what the phenotype is. This value will be N/A if a description file is not provided, if the phenotype doesn't have a description, or if a phenotype file is not provided.

----

* **\*_case_count_in_network**: Number of individuals in the network that are affected by the phenotype. 

----

* **\*_cases_in_network**: Comma-separated list of individual IDs in the network that are cases for the phenotype.

----

* **\*_excluded_count_in_network**: Number of individuals in the network that are excluded from the statistical analysis for the phenotype.

----

* **\*_excluded_in_network**: Comma-separated list of individual IDs in the network that are excluded from the statistical analysis for the phenotype.

----

* **\*_pvalue**: Pvalue determined for the specific phenotype

.. note::

    The final five columns, "\*_case_count_in_network, \*_cases_in_network, \*_excluded_count_in_network, \*_excluded_in_network, \*_pvalue" are only created if the user provides a case file, otherwise the output file will only have the first 11 columns. If the user provides a case file then these five columns will be created for each phenotype so if you provided 3 phenotypes then 15 columns would be added to the output file.

.. note::

    If the user passes the ``--compress-output`` flag, the output file will be gzipped and have the suffix ".drive_networks.txt.gz".

.. note::

    If the user passes the ``--split-phecode-categories`` flag, the output will be broken into a separate file for each phecode category. Each file follows the naming pattern ``{output}.{category}.drive_networks.txt`` and still contains the base network columns along with the minimum phecode columns.


*Log File*
``````````

DRIVE creates a log file with whatever name the user provides. This file has the suffix ".log". This file has information about the arguments the user passed and then runtime information from the program such as how many networks were identified and how many haplotypes were identified. The amount of information written to this file will vary depending on what level of verbosity the user chooses.


DRIVE dendrogram command output:
--------------------------------

The dendrogram subcommand also outputs two files. One of which is the same log file as described in the previous section. The other file is a png image called "network\_#_dendrogram.png" made for either the network of interest or all the networks in the input file. These images are saved in the specified output directory.

If the user provides the "--keep-temp" flag then an extra directory is created inside the output directory called "network\_#_temp". This subdirectory will contain the network specific distance matrix that is used to generate the dendrogram.

If the user provides the "--map-ids" flag then an additional file is created called "network\_#_id_mappings.txt". This file contains a mapping of the original individual IDs to anonymized IDs of the form "patient_X". This mapping is useful when preparing dendrograms for publication to protect individual identities.
