This software is made available under Apache Licence, version 2.
http://www.apache.org/licenses/LICENSE-2.0.html

# Candidates Python
## Background
The function of this application is to collect the reviewed UniProtKB proteins recognised by different InterPro Family signatures and to ouput blocks of text showing how consistent the annotations are among these protein records.

InterPro coordinates the world-wide effort to characterise proteins using sequence models known as signatures. InterPro does not itself create signatures, but groups signatures from the different InterPro member databases into sets which then receive an InterPro identifier. So for instance, the InterPro identifier IPR000006 is made up of Prints PR00860 and Panther PTHR23299.

UniRule is a system for annotation of proteins in UniProtKB which uses InterPro identifiers, or signatures from the individual member databases to group proteins of known function together, so that this information can be propagated across the very large number of protein records in UniProtKB which have no known function, but do have positive matches for the signatures in InterPro.

Periodically it is helpful to create a list of candidate InterPro signatures that are not already used to propagate annotation, and which can be shown to be effective in grouping known proteins into sets with consistent functional properties.

## Run Types: Demo and Main
### Demo
The default run mode is 'demo', which will run in a few minutes on a limited set of data already stored in: ``data/demo/input/``

The demo code can be invoked from anywhere on Unix with:   
``path_to/CandidatesPython/bin/candidates.sh``  
or  
 ``path_to/CandidatesPython/bin/candidates.sh demo``  

On Windows make sure the file  
``CandidatesPython/bin/candidates_demo.bat``   
is executable and double click, or invoke  
``path_to/CandidatesPython/bin/candidates_demo.bat``  
on the command line from any location.

### Main
The main version will take an hour or two to run and will download a lot of data - mostly because of all the look up of records via the public UniProtKB data service. **To run the main version, two files need to be collected and placed in the folder**  
``CandidatesPython/data/main/input/``

**File 1** is the public xml for the latest release of InterPro (https://www.ebi.ac.uk/interpro/) which is about 145 MB after unzipping. On Unix:   
``cd CandidatesPython/data/main/input``  
``wget ftp.ebi.ac.uk/pub/databases/interpro/current/interpro.xml.gz``  
``gunzip interpro.xml.gz``  

**File 2** is the current set of rules used by UniRule, which is made available on the public UniProt ftp server (ftp://ftp.ebi.ac.uk/pub/contrib/UniProt/UniFIRE/rules/unirule-urml-latest.xml) . This file is about 40MB. On Unix:  
``cd CandidatesPython/data/main/input``  
``wget ftp://ftp.ebi.ac.uk/pub/contrib/UniProt/UniFIRE/rules/unirule-urml-latest.xml``  

## What happens during a run?
All the calculations are run following the initial command, but the code executes in four distinct stages. The first two are quick, the third is very slow, and the fourth is reasonably fast.

### Stage 1 Checking user setup
The application checks that the user is running Python 3.5 or above and that the required files are in the input folders. If not the application exits.

### Stage 2 Generating a list of candidate protein signatures
The contents of the input xml files is parsed to:
-  Create a mapping between InterPro identifiers and the Interpro member database signatures.
-  Create a mapping between InterPro identifiers and the InterPro type (eg Family, Domain, Site, etc)
-  Filter the InterPro identifiers for Families and remove any that are listed in the InterPro xml file as contain other InterPro ids as children.
- Collect all the InterPro signatures from the UniRule xml file that are already used as positive conditions in UniRule rules.
- These files are saved in the output folder for checking if necessary, and are used to generate the list of candidate InterPro signatures.
- The final list of InterPro identifiers contains:
   -  No InterPro signature that contain other InterPro identifiers as children
   -  No InterPro signature that contains an InterPro member database signature that is already used in UniRule rule as a positive condition.
   -  No signatures that come from the Hamap or PIR protein signature databases (this is to avoid overlap between work at the EBI and the two other consortium members of UniProt).

### Stage 3 Filtering by the number of reviewed and unreviewed hits
For each of the candidate InterPro signatures in this list, the application looks up the number of reviewed protein entries and the number of unreviewed protein entries recognised by the signature. This takes a while as the UniProt REST API is queried to return a JSON object which contains a lot of other information as well.  
Only those signatures which recognise 10 or more reviewed entries, and 100 or more unreviewed entries are kept. If there are fewer reviewed entries the reliability of and rule for propagating annotation will be reduced. If less than 100 unreviewed entries are recognised the benefit of creating the UniRule rule is marginal.  

### Stage 4 Collecting and analysing the annotation 
In the final stage the annotation found in the reviewed records identified by each of the candidate signatures is collected. This annotation is then divided into the different main taxonomic groups present, and the consistency of annotation within each taxonomic group is checked. Where the annotation is at least 90% consistent,  the application saves the data to the output file.

### The final output

The format of the output file is as shown below.  The six columns are:
Kingdom
Major Taxonomy
Code for the annotation (eg CCFU = Function, SPKW = Keyword)
Number of reviewed in this taxonomic group
Number of records that have identical annotation
Annotation text


\# IPR004090  Reviewed 54, Unreviewed 105245
|Kingdom|MajorTaxon|Code|Reviewed|Unreviewed|AnnotatonText|
|---|---|---|---|---|---|
|Bacteria |Thermotogae    |CCFU    |3    |3    |Chemotactic-signal transducers respond to changes in the concentration of attractants ...|
|Bacteria |Thermotogae    |CCLO    |3    |3    |Cell membrane|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Cell membrane|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Chemotaxis|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Complete proteome|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Membrane|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Methylation|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Reference proteome|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Transducer|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Transmembrane|
|Bacteria |Thermotogae    |SPKW    |3    |3    |Transmembrane helix|
|Bacteria |Proteobacteria    |SPKW    |26    |24    |Complete proteome|
|Bacteria |Proteobacteria    |SPKW    |26    |24    |Reference proteome|
|Bacteria |Proteobacteria    |SPKW    |26    |25    |Transducer|
|Bacteria |Proteobacteria    |SPKW    |26    |24    |Membrane|
|Bacteria |Proteobacteria    |SPKW    |26    |24    |Transmembrane|
|Bacteria |Proteobacteria    |SPKW    |26    |24    |Transmembrane helix|
|Archaea |Euryarchaeota    |SPKW    |19    |19    |Transducer|
|Bacteria |Cyanobacteria    |DERF    |1    |1    |Putative methyl-accepting chemotaxis protein sll0041|
|Bacteria |Cyanobacteria    |CCSI    |1    |1    |Belongs to the phytochrome family|
|Bacteria |Cyanobacteria    |SPKW    |1    |1    |Complete proteome|
|Bacteria |Cyanobacteria    |SPKW    |1    |1    |Reference proteome|
|Bacteria |Cyanobacteria    |SPKW    |1    |1    |Repeat|
|Bacteria |Cyanobacteria    |SPKW    |1    |1    |Transducer|
|Bacteria |Firmicutes    |CCLO    |5    |5    |Cell membrane|
|Bacteria |Firmicutes    |SPKW    |5    |5    |Cell membrane|
|Bacteria |Firmicutes    |SPKW    |5    |5    |Complete proteome|
|Bacteria |Firmicutes    |SPKW    |5    |5    |Membrane|
|Bacteria |Firmicutes    |SPKW    |5    |5    |Transducer|
|Bacteria |Firmicutes    |SPKW    |5    |5    |Transmembrane|
|Bacteria |Firmicutes    |SPKW    |5    |5    |Transmembrane helix|






