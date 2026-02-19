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

An example file can also be found in the "tests/test_inputs" folder of the repository called "test_phenotype_file_withNAs.txt"

Command to run DRIVE phenome-wide:
----------------------------------
When you provide a phenotype file with multiple columns, DRIVE will automatically start to run the analysis phenome-wide without any additional flags.

.. code:: python

  drive cluster \
    -i tests/test_inputs/simulated_ibd_test_data_v2_chr20.ibd.gz \
    -f hapibd \
    -t 20:4666882-4682236 \
    -o ./test_drive_phenomewide_output \
    --min-cm 3 \
    --cases tests/test_inputs/test_phenotype_file_withNAs.txt \
    --segment-overlap overlaps \
    --min-network-size 2 \
    --recluster \
    --log-to-console \
    --log-filename test_drive_phenomewide_output.log

When finished, DRIVE will create a output file that has five columns for each phenotype. An example output file can be found here "tests/test_outputs/test_drive_phenomewide_output.drive_networks.txt". The first few rows of this output are shown below:

.. csv-table:: DRIVE Phenomewide Output Example
   :header-rows: 1
   :widths: auto
   :delim: |

   clstID|n.total|n.haplotype|true.positive.n|true.positive|falst.postive|IDs|ID.haplotype|min_pvalue|min_phenotype|min_phenotype_description|CV_414_case_count_in_network|CV_414_cases_in_network|CV_414_excluded_count_in_network|CV_414_excluded_in_network|CV_414_pvalue|NS_324.11_case_count_in_network|NS_324.11_cases_in_network|NS_324.11_excluded_count_in_network|NS_324.11_excluded_in_network|NS_324.11_pvalue|phenoC_case_count_in_network|phenoC_cases_in_network|phenoC_excluded_count_in_network|phenoC_excluded_in_network|phenoC_pvalue
   0|4|4|4|0.6667|0|842,130,30,861|130.1,842.1,30.2,861.2|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   1|2|2|1|1.0000|0|223,443|223.1,443.1|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   2|2|2|1|1.0000|0|253,957|253.2,957.1|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|1|253|1|1|253|0|None|1
   3|3|3|3|1.0000|0|244,531,231|231.1,244.1,531.2|N/A|N/A|N/A|0|N/A|0|None|1|1|531|0|None|1|0|N/A|0|None|1
   4|5|5|7|0.7000|0|574,676,210,535,94|535.1,574.2,94.1,210.1,676.2|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   5|3|3|3|1.0000|0|600,962,591|591.2,600.2,962.2|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   6|2|2|1|1.0000|0|610,895|610.1,895.2|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   7|4|4|5|0.8333|0|342,295,211,969|211.1,969.2,342.1,295.1|N/A|N/A|N/A|0|N/A|0|None|1|1|211|0|None|1|0|N/A|1|295|1
   8|3|3|3|1.0000|0|133,622,941|622.2,941.1,133.1|N/A|N/A|N/A|0|N/A|0|None|1|1|941|0|None|1|0|N/A|0|None|1
   9|6|6|15|1.0000|0|484,577,946,343,10,609|343.2,609.1,946.2,484.2,10.1,577.2|N/A|N/A|N/A|0|N/A|1|10|1|1|10|0|None|1|0|N/A|0|None|1
   10|6|6|12|0.8000|0|786,259,533,199,575,811|533.1,786.1,199.1,575.2,811.1,259.2|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   11|2|2|1|1.0000|0|801,938|801.2,938.1|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|1|801|1
   12|2|2|1|1.0000|0|871,895|871.2,895.1|N/A|N/A|N/A|1|871|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   13|5|5|8|0.8000|0|773,108,751,970,326|108.2,970.2,326.2,773.2,751.1|N/A|N/A|N/A|0|N/A|0|None|1|0|N/A|0|None|1|0|N/A|0|None|1
   14|5|5|10|1.0000|0|385,711,14,615,507|14.2,615.2,385.1,507.1,711.2|0.34684049957692414|NS_324.11|Parkinson's disease (Primary)|0|N/A|0|None|1|2|615, 385|0|None|0.34684049957692414|0|N/A|0|None|1

