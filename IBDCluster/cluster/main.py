from typing import Generator, List, Set
from collections import namedtuple
from dataclasses import dataclass, field
import os
import models
@dataclass
class Grids_Found:
    ids_found: Set[str] = field(default_factory=set)
    new_grids: List[str] = field(default_factory=list) # This attribute will be a list of all new grids found during each cluster iteration
    all_grids_found: Set[str] = field(default_factory=set) # This attribute will be a set of all nthe grids found during the entire clustering

def load_gene_info(
    filepath: str
    ) -> Generator:
    """Function that will load in the information for each gene. This function will return a generator
    
    filepath : str
        filepath to a file that has the information for the genes of interest
        
    Returns
    
    Generator
        returns a generator of namedtuples that has the gene information
    """
    Genes =  namedtuple("Genes", ["name", "chr", "start", "end"])

    with open(filepath, "r") as gene_input:

        for line in gene_input:
            split_line: List[str] = line.split()

            gene_tuple: Genes = Genes(*split_line)

            yield gene_tuple


def get_ibd_program(ibd_program: str):
    """Function that will take whatever ibd program the user pass and will get the correct info object for it
    
    Parameters
    
    ibd_program : str
        string of either 'hapibd' or 'ilash'
        
    Returns
    
    Object
        returns either a clusters.Hapibd_Info object or clusters.Ilash_Info object
    """
    if ibd_program == "hapibd":
        return models.Hapibd_Info()
    else:
        return models.Ilash_Info()

def filter_region(start: int, end: int) -> pd.DataFrame:
    pass

def cluster(
    ibd_program: str, 
    gene_info_filepath: str
    ) -> None:
    """Main function that will handle the clustering into networks"""

    # we will need the information for the correct ibd_program
    indices: models.File_Info = get_ibd_program(ibd_program)

    # creating a generator that returns the Genes namedtuple from the load_gene_info function
    gene_generator: Generator = load_gene_info(gene_info_filepath)

    for gene_tuple in gene_generator:

        hapibd_file:str = indices.find_file("".join(["chr", gene_tuple.chr]))

        pass