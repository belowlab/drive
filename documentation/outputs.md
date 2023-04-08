---
layout: default 
title: Outputs
parent: Documentation
nav_order: 3
---
# Output File:
---

DRIVE outputs a file that ends in .DRIVE.txt. This file has the results of the clustering analysis. The file begins with two lines that tell how many IBD segments and haplotypes were identified as well as how many clusters were identified. There are eight columns in the output file like the table below. 

| clustID |    n.total     | n.haplotype | true.positive.n | true.positive | false.positive |       IDs       |     ID.haplotype      | 
|:--------|:---------------|:------------|:----------------|:--------------|:---------------|:----------------|:----------------------|
|    #    |        #       |      #      |      #          |      #        |         #      | grids in network| haplotypes in network |   

### Column descriptions:
---
* <span style="color: #F0FF00">**clustID**:</span> ID given to each network identified. This value will have the form "clst#".

---
* <span style="color: #F0FF00">**n.total**:</span> Total number of individuals in the network.

---
* <span style="color: #F0FF00">**n.haplotype**:</span> The number of haplotypes in the network. This value may be different than n.total due to inbreeding.

---
* <span style="color: #F0FF00">**true.positive.n**:</span> Number of shared IBD segments that are identified in the network. 

---
* <span style="color: #F0FF00">**true.postive**:</span> Proportion of identified IBD segments in networks vs the total number of possible IBD segments that could exist between all individuals in the network.

---
* <span style="color: #F0FF00">**false.postive**:</span> Proportion of individuals within the cluster that share an IBD segment with another individual outside of the cluster.

---
* <span style="color: #F0FF00">**IDs**:</span> List of ids that are in the network. 

---
* <span style="color: #F0FF00">**ID.haplotype**:</span> List of haplotypes that are in the network. These will be equivalent to the ids in the "IDs" column except each id will have a phase value attached to it.