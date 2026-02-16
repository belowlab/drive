.. .. raw:: html

..     <style> .yellow {color:yellow; font-weight:bold;} </style>

.. .. role:: yellow

Running DRIVE phenomewide
=========================
This section illustrates how to run DRIVE for multiple phenotypes or diseases of interest in the same analysis. This process will be referred to as a PheWES (Phenome-wide Enrichment Study) throughout the documentation.

This process is very similar to the how we would run DRIVE and can be illustrated in the following steps:

1. Identify pairwise IBD segments in the cohort of interest
2. Generate a phenotype file containing multiple phenotypes of interest
3. Run DRIVE over the locus of interest

For this example we are going to assume that IBD segments have already been detected using a program such as hap-IBD or iLASH. 


Format of the Phenotype File:
-----------------------------
The biggest difference in running DRIVE phenomewide is that the input phenotype file takes the form of a matrix where the first column is the cohort IDs and every other column in the file is phenotype of interest. This file should be tab separated. Excluded individuals for any phenotype can be represented by N/A or -1.

.. list-table:: Example of a phenotype file with multiple phenotypes (completely made up)
   :widths: 20 20 20 20
   :header-rows: 1

   * - GRID
     - status_1
     - status_2
     - status_3
   * - ID1
     - 1
     - 0
     - -1
   * - ID2
     - 0
     - 1
     - 0
   * - ID3
     - 1
     - 1
     - -1
   * - ID4
     - 0
     - 0
     - 1


Command to run DRIVE phenomewide:
---------------------------------
When you provide a phenotype file with multiple columns, DRIVE will automatically start to run the analysis phenomewide without any additionally flags.

.. code:: python

  drive cluster \
    -i $input_file \
    -f hapibd \
    -t $region \
    -o $output_file \
    --min-cm 3 \
    --cases $PHENO_FILE \
    --segment-overlap overlaps \
    --min-network-size 2 \
    --recluster \
    --log-to-console \
    --log-filename $log_filename 
