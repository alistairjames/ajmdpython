
# Candidates Python
## Background
This code is all about protein records held in the UniProt Knowledgebase (UniProtKB) which is the main international database of proteins, and is a collaboration between the European Bioinformatics Institute (EBI), the Swiss Institute for Bioinformatics (SIB) and the Protein Information Resource at Georgertown University (PIR).

There are a lot of records in the database (180 million), most of which are simply proteins predicted to exist because protein coding genes have been detected in DNA sequences with the help of bioinformatics software.

For a small proportion of the records (550k), there is good data on their functional properties. Some have been carefully experimentally characterised, the protein has been isolated and a protein structure determined. Others have very close sequence similarity to proteins whose function is understood, so their function can be assigned with confidence.

A big part of the management of UniProtKB is providing descriptions of the function and properties of the 179.5 million uncharacterised proteins. Essentially this is a data-mining exercise, in which sequence patterns and features in the proteins are used to categorise the proteins of known function, after which functional information is propagated to proteins of unknown function which share the same sequence features.

InterPro is the database that holds the information on all these sequence features, commonly called signatures. Many research groups contribute to InterPro by creating signatures, and InterPro organises their contributions into a coherent database by grouping signatures from different researchers that recognise the same sets of proteins into one group identified by a unique InterPro identifier.

UniProt then takes these InterPro identifiers, and the signatures that they contain and uses them in several different systems for annotating the 179.5 million predicted proteins.

This code is about one of those prediction systems, known as UniRule. UniRule is a rules-based system, where the consistency of the properties of proteins recognised by a signature is manually reviewed before the signature is used to propagate functional annotation to unknown proteins

So this application is called CandidatesPython because it is using Python to search programmatically for signatures which are good candidates for use in a UniRule rule. Running this application saves a lot of wasted effort looking at signatures which do not have matches with consistent annotation among the known proteins, and so are not useful for propagating annotation.

In practice, the application does the following:  
 - Collects all the currently available InterPro identifiers
 - Discards those that have been used before in UniRule rules
 - Collects all the reviewed UniProtKB proteins recognised these InterPro identifiers
  - Discards the InterPro identifiers which do not match enough reviewed protein records.
 - Extracts the annotation from the reviewed records and reorganises it by taxonomic group
 - Determines if the annotation is consistent for each of these taxonomic groups and outputs the annotation to a file as a block of text.  
 
 This file then contains the set of candidate signatures that those creating rules can work from with some hope of success.
 
 

## Run Types: Demo and Main
### Demo
The default run mode is 'demo', which will run in a few minutes on a limited set of data already stored in: ``data/demo/input/``

The demo code can be invoked from anywhere on Unix with:   
``path_to/CandidatesPython/bin/candidates.sh``  
or  
 ``path_to/CandidatesPython/bin/candidates.sh demo``  

On Windows the code runs fine from within a Python shell running Python 3.5.  
In the shell navigate to 
``CandidatesPython``  
then run the command:  
``python -m candidates.candidates_main demo ``  
(the file ``bin\candidates.bat`` is currently only working my personal installation of Python)

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

After this the code is run with:
``path_to/CandidatesPython/bin/candidates.sh main``  on linux  
and  
``python -m candidates.candidates_main main ``   from the CandidatesPython folder within a Python shell on Windows.

## What happens during a run?
All the calculations are run following the initial command, but the code executes in four distinct stages. The first two are quick, the third is very slow, and the fourth is reasonably fast.

### Stage 1 Checking user setup
The application checks that the user is running Python 3.5 or above and that the required files are in the input folders. If not the application exits.

### Stage 2 Generating a list of candidate protein signatures
The contents of the input xml files is parsed to:
-  Create a mapping between InterPro identifiers and the InterPro member database signatures.
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

The format of the output file is as shown below.  
(Codes: CCFU function; CCLO subcellular location; SPKW keyword; DERF recommended full name; CCSI protein family)

\# IPR004090  Reviewed 54, Unreviewed 105245
|Kingdom|MajorTaxon|Code|Reviewed|SameAnnotation|AnnotationText|
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






