# File will have different Interfaces used in the program as well as different class for types. This will simplify the imports and allow me to reduce coupling between modules

from collections import namedtuple

# namedtuple that will contain information about the gene being run
Genes = namedtuple("Genes", ["chr", "start", "end"])
