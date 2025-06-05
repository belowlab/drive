## Unreleased

## v3.0.0 (2025-06-04)

### Feat

- **generate_dendrogram.py**: finished implementing the dendrogram subcommand
- **generate_dendrogram.py**: Began to create the logic to construct dendrograms from the DRIVE output files
- **network_algorithm.py**: moved relevant code for the network algorithm into its own folder
- **dendrogram**: Adding the ability to generate a dendrogram from the drive networks

### Fix

- **dendrogram_subcommand.py**: fixed a type annotation to be compatible with python 3.9
- **testing-and-parser/__init__.py**: added integration test for dendrogram functionality and fixed bug where isort messed up imports

## v2.7.15 (2025-04-25)

## v2.7.15b1 (2025-04-24)

### Fix

- **pvalues.py**: updated the size of the network to reflect removal of proband

### Refactor

- **pyproject.toml**: updated the logging module to pull it from pypi
- **logging**: added a log message to report the drive version

## v2.7.15a0 (2025-02-20)

### Refactor

- **cluster.py**: Changed the minimum network size to be more intuitive and allow reporting of 2 person networks

## v2.7.14 (2025-01-16)

### Fix

- **cluster.py**: removed the print statements that were clogging the screen
- **filter.py**: removed the chromosome check

## v2.7.10 (2025-01-16)

### Fix

- **filter.py**: Original fix didn't work. Forgot that the attribute was a named tuple and is immutable. Also realized I don't need to update the value because the downstream filter using it was redundant. Only updated the check and the logging message
- **filter.py-and-pyproject.toml**: Adjust code so that chromosomes can also use chr prefix

## v2.7.6 (2024-10-13)

### Fix

- **filter.py**: Couldn't read in build 38 data where the chromosome has prefix chr
- **Dockerfile**: Fixed the docker file to use the debian:12.6 image

## v2.7.4 (2024-07-16)

### Feat

- drive now writes out the exclusion IDs to a column

### Fix

- **case_file_parser.py**: Made sure fillna was inserting integer not string which was affecting the exclusion counts
- **case_file_parser.py**: Fixed an issue with how the dictionary was being built with all the keys even if we only wanted one phenotype

### Refactor

- **filter.py**: added a message that tells how many individuals from the phenotype file were actually found in the IBD files
- **drive.py**: remove unnecessary logging statements
- **case_file_parser.py**: removed print statement that was used for debugging
- **drive.py**: added a flag to show version of drive being used
- **data_container.py**: adjusted the type hint to reflect the fact that the grid list is actually a set and not a list
- **filter.py**: Changed a description message of how many pairs were found

## v2.6.1 (2024-03-18)

### Fix

- fixed issue where no segments were being found

## v2.6.0 (2024-03-18)

### Feat

- **case_file_parser.py**: Added a way to specify a specific phecode column
- **case_file_parser.py**: Changed the parser to use xopen for better performance

### Refactor

- fixed styling errors and a type annotation
- **case_file_parser.py**: changed to using pandas in the parser because it is more efficient
- removed the xopen dependencies because it might have been slower than open
- **pyproject.toml**: updated the version number

## v2.3.3 (2024-02-23)

### Feat

- **case_file_parser.py**: added ability to specify one phenotype column in a matrix

### Fix

- **ClusterHandler.redo_clustering**: bug caused when no individuals shared pairwise IBD segments and graph was improperly formed
- **IbdFilter**: for the id columns to be read in as string when reading ibd file chunks
- **case_file_parser.py**: Fixed a bug where the case file parser was not identifying the appropriate index if the user only wished to find a specific haplotype

### Refactor

- **drive.py**: fixed a typer in the recluster flag help message

## 2.2.0 (2023-11-27)

### Feat

- switched from using typer to just argparse

### Fix

- **case_file_parser.py**: fixed bug that the wrong method was called on a set

### Refactor

- linted the filter.py file

## 2.1.3 (2023-09-27)

### Feat

- Made sure that the program supports build38 ibd files

### Fix

- **cluster.py**: fixed a bug that caused the IDs to mismatch

## 2.1.1 (2023-08-28)

## 2.1.0 (2023-08-10)

### Feat

- **pvalues.py**: added an output column that describes which cases are in the network for a specific phenotype

### Fix

- **cluster**: fixed a bug in the clustering where the incorrect ids were being used to cluster
- **config.json**: updated the module paths to be correct which meant importing from drive first
- **pvalues.py**: updated the factory import to use the module

### Refactor

- **pvalues.py**: when there is no overlap between the network members and the cohort cases then I added a section to just write N/A instead of a blank spot to be consist with prior design decisions
- **callbacks.py**: moved config.json into drive src folder so that it will be included in the pypi build (hopefully).

## 2.0.8 (2023-07-03)

### Refactor

- **filter.py**: removed unnecessary print statements

## 1.0.0 (2023-06-30)

### Feat

- Added an overlap filter
- **segment-filtering**: started add functionality to filter.py for overlapping segment filtering
- **segment-filtering**: Add an option to filter to segments that overlap target loci and not just those that contain the segment

### Fix

- **generate_indices.py**: fixed the index for the cM column in ILASH model to be correct
- **network_writer**: correct how the output file name is made when it contains a period
- **pvalue**: fixed a bug in pvalue.py where the phenotype percentage was not calculated properly

## v2.0.2 (2023-05-15)

### Fix

- fixed bug where the loglevel was not being reset to the original one in the record_inputs method
- fixed cases when there are no controls
- Fixed a bug where the header line was appending a new line incorrectly

### Refactor

- log situation where ibd_pd is empty and early termination of program
- Add a check to see if dataframe is empty after filtering for individuals. If so then it continues to next loop
- **logging**: Added more informative debug logging to the case_file_parser.py
- switched list in phenotype dictionary to sets
- adding more informative logging statements
- make sure that the ibd file matches the chromosome of the chromosome target
- updated the exclusion criteria so it includes blank spaces

### Perf

- updated set operations

## v2.0.1 (2023-05-05)

### Fix

- Fixed typos that were messing with the pvalue calculation

### Refactor

- **logging**: Fixed the record_inputs method of the logger so that now it records the inputs and writes it to a file
- **logging**: Changed the code to adapt to the new OOP logger style

## v2.0.0 (2023-05-04)

### Fix

- Removed duplicate values from the ibd_vs attribute of the IbdFilter

### Refactor

- Finished refactoring drive
- refactor filter to remove unnecessary function and to determine all individuals in cohort
- **plugins**: Added a config file for the plugin systemm to specify what plugins exist
- **plugins**: Setup the plugin architecture
- Updated poetry lock file for dependencies
- **clustering**: Finished refactoring the clustering module
- Created models for the Data class and the network class
- removed the accidental file
- moved callbacks into utilities modules
- Added the load_phenotype_descriptions to the __init__.py
- Added a function called load_phenotype_descriptions that will read in the phecode descriptions file if the user passes it
- Added attribute to keep a list of all individuals in cohort
- **phenotyping**: adjusted the phenotype parser to support multiple phenotypes
- **phenotypeing**: refactored how phenotype files are read in to determine case, control, or exclusion individuals
- fixed merge conflict in .gitmodules
- merging the proper changes
- **clustering**: finished first refactor of the clustering algorithm
- Added jupyter notebook as dependency group to test.
- **igraph-clustering**: Fixed clustering bug
- **logging**: changed log levels to be 1 or 2 to reflect typers use of -v or -vv
- started adding in the redo clustering steps to the code
- Adjusted the imports
- Made sure to reset the index so that the dataframe is the same as the original code
- **PhenotypeFileParser**: added functionality to the parser so it can determine cases/controls/exclusions
- **gitignore**: Add the /tests/test_input directory to version controls
- **logging**: Changed the logging in the filter.py file
- **name-change**: Changed the filter module to filters to avoid name collision with filter function
- Added a directory for utility functions.
- **clustering**: Broke the Networks class into two classes
- **clustering**: Finished the initial cluster step and fixed the missing attribute in igraph 0.10.4
- Created the clustering class and wrote functionality for the initial clustering step
- Starting refactoring the clustering and reorganizing the models
- **type-hints**: using type hints from Typing module
- **Error-Handling**: updated the Filter._remove_dups method to raise a KeyError if columns aren't present

## 1.1.0 (2023-04-04)

### Feat

- **logging**: added a logging submodule

### Refactor

- **logging**: Added a submodule for logging
- **filtering-ibd-file**: Restructured hung-hsin's filtering into a module
- **logging**: added logging to the program
- **log**: removed the messed up log folder
- removed the log from the .gitmodules
- **debugging**: added a __str__ method to indices classes

## v1.0.0 (2023-03-31)

### Refactor

- **DRIVE.py**: moved DRIVE.py to drive.py and added a pre-commit hook
- **global-variables**: removed more global variables
- **global-variable-removal**: removed some global variables that were constants and converted them to user options in the commandline
- **drive/generate_indices.py**: remove branching in create_indices
- **file-indices**: Switched to a strategy pattern
- **split_target_string**: Added a check to the split_target_string function
- **drive/DRIVE.py**: refactor how the target string was split and how to indices are created
- **drive/callbacks.py**: created callback function to make sure that the input ibd file exist
- **DRIVE.py**: Refactored CLI to use typer-cli
- **profiles/python_3_8_drive_dcm_hh.prof**: addeed a profile for python 3.8
- **pyproject.toml**: Added static type checkers and linters

## 1.0.1 (2023-03-26)

### Perf

- **profiles**: added directory to keep track of profiles
