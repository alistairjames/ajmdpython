"""
This code goes through a list of InterPro signatures and:
1. Collects the public reviewed records containing the signature in json format,
2. Extracts the annotations for each record,
3. Groups the records by taxonomy,
4. Tests if the annotations in a taxonomic group are 90% or more consistent with each other
5. If there are consistent annotations, writes to file the InterPro signature and the consistent annotations

Output format:

# InterProId / Reviewed / Unreviewed
TaxonomicGroup / AnnotationCode / Total / Consistent / AnnotationText

Example:

# IPR000074  Reviewed: 115  Unreviewed: 2920
Eukaryota Metazoa	CCLO	115	115	Secreted
Eukaryota Metazoa	CCSI	115	115	Belongs to the apolipoprotein A1/A4/E family
Eukaryota Metazoa	SPKW	115	113	HDL
Eukaryota Metazoa	SPKW	115	114	Lipid transport
Eukaryota Metazoa	SPKW	115	107	Repeat
Eukaryota Metazoa	SPKW	115	115	Secreted
Eukaryota Metazoa	SPKW	115	114	Signal
Eukaryota Metazoa	SPKW	115	114	Transport

"""

import sys
import json
import candidates.utils as utils
from copy import deepcopy
import traceback
import logging
logger = logging.getLogger(__name__)

annotation_list_types = ['SPOC', 'DERS', 'DEEC', 'DEAF',
                         'CCCA', 'CCCO', 'CCFU', 'CCLO',
                         'CCPA', 'CCSI', 'CCSU', 'SPKW']

annotation_string_types = ['accession', 'DERF',  'GNNM']

excluded_keywords = ['Complete proteome', ]


def collect_candidates_from_list_with_counts(infilepath, outfilepath):
    signature_with_counts_list = [line.rstrip() for line in open(infilepath)]
    logger.info(f'Starting to collect candidate rules from {len(signature_with_counts_list)}  InterPro signatures')

    outfile = open(outfilepath, 'w')
    outfile.write('# Columns: TaxonomicGroup / AnnotationCode / Total / Consistent / AnnotationText\n')
    count = 0
    for signature_line in signature_with_counts_list:
        signature, reviewed, unreviewed = signature_line.split('\t')
        count += 1
        if count % 20 == 0:
            logger.info(f'Data collected for {count} candidate signatures')
        # this gets a single json object containing several uniprot records
        jsonrecords = get_reviewed_uniprot_jsons_from_interpro_id(signature)
        # update the reviewed count read in to signature_with_counts_list from infilepath
        reviewed = len(jsonrecords)
        taxonomy_groups = group_records_by_taxonomy_from_json(jsonrecords)
        text = '\n# {0}  Reviewed: {1}  Unreviewed: {2}'.format(signature, reviewed, unreviewed)
        outfile.write(text + '\n')
        for taxon in taxonomy_groups:
            annotation_collection = get_json_data_grouped_by_annotations(taxonomy_groups[taxon])
            consistent_annotations = get_consistent_annotations(annotation_collection)
            output_taxonomy_annotation_collection(taxon, consistent_annotations, outfile)

    outfile.close()
    logger.info(f'Data collected for {count} candidate signatures')


# Structure of annotations is a dictionary with either single terms or a list of terms
def extract_annotations(record_json):
    # Add placeholders for all the possible keys
    record = {}
    for a in annotation_list_types:
        record[a] = []
    for a in annotation_string_types:
        record[a] = ''

    record['accession'] = record_json['accession']
    record['SPOC'] = record_json['organism']['lineage']
    protein = record_json['protein']
    if 'recommendedName' in protein:
        recnames = protein['recommendedName']
        record['DERF'] = recnames['fullName']['value']
        if 'shortName' in recnames:
            for s in recnames['shortName']:
                record['DERS'].append(s['value'])

        if 'ecNumber' in recnames:
            for ec in recnames['ecNumber']:
                record['DEEC'].append(ec['value'])

    if 'alternativeName' in protein:
        altnames = record_json['protein']['alternativeName']
        for alt in altnames:
            record['DEAF'].append(alt['fullName']['value'])

    # only one gene name collected
    if 'gene' in record_json:
        if 'name' in record_json['gene'][0]:
            record['GNNM'] = record_json['gene'][0]['name']['value']

    if 'comments' in record_json:
        try:
            collect_comments(record, record_json['comments'])
        except:
            logger.error(f"Failed extracting Comments from {record_json['accession']}")
            traceback.print_exc(file=sys.stdout)
            sys.exit(0)

    if 'keywords' in record_json:
        for kw in record_json['keywords']:
            if kw not in excluded_keywords:
                record['SPKW'].append(kw['value'])

    return record


def collect_comments(record, comment_json):
    for comment in comment_json:
        ctype = comment['type']
        if ctype == 'CATALYTIC_ACTIVITY':
            reaction = comment['reaction']
            name = reaction['name']
            rhea = 'None'
            if 'dbReferences' in reaction:
                for xref in reaction['dbReferences']:
                    if xref['type'] == 'Rhea':
                        rhea = xref['id']
                        break
            record['CCCA'].append('{0} {1}'.format(rhea, name))

        elif ctype == 'COFACTOR':
            if 'cofactors' in comment:
                for cofactor in comment['cofactors']:
                    name = cofactor['name']
                    chebi = 'None'
                    if 'dbReference' in cofactor:
                        if cofactor['dbReference']['type'] == 'CHEBI':
                            chebi = cofactor['dbReference']['id']
                    record['CCCO'].append('{0} {1}'.format(chebi, name))
            if 'text' in comment:
                #print('Cofactor Text ' + record['accession'])
                for commenttext in comment['text']:
                    record['CCCO'].append(commenttext['value'])

        elif ctype == 'FUNCTION':
            for text in comment['text']:
                record['CCFU'].extend(text['value'].split('. '))

        elif ctype == 'SUBCELLULAR_LOCATION':
            if 'locations' in comment:
                for location in comment['locations']:
                    record['CCLO'].append(location['location']['value'])
            if 'text' in comment:
                #print('SubcellularLocation Text ' + record['accession'])
                for locationtext in comment['text']:
                    record['CCLO'].append(locationtext['value'])

        elif ctype == 'PATHWAY':
            for text in comment['text']:
                record['CCPA'].append(text['value'])

        elif ctype == 'SIMILARITY':
            for text in comment['text']:
                record['CCSI'].append(text['value'])

        elif ctype == 'SUBUNIT':
            for text in comment['text']:
                record['CCSU'].append(text['value'])


# Converts a json object containing records into a dictionary with key: taxonomy_group and value: list of records
def group_records_by_taxonomy_from_json(json):
    taxongroups = {}
    for item in json:
        record = extract_annotations(item)
        taxon = ' '.join(record['SPOC'][:2])
        if taxon not in taxongroups:
            taxongroups[taxon] = []
        taxongroups[taxon].append(record)
    return taxongroups


def get_json_data_grouped_by_annotations(json_list):
    # Add all the annotations
    annotation_collection = {'accession_list': [], 'taxonomy': set()}
    for record in json_list:
        annotation_collection['accession_list'].append(record['accession'])
        annotation_collection['taxonomy'].add(' '.join(record['SPOC'][:2]))

    for atype in ['DERF', 'GNNM']:
        annotation_collection[atype] = {}
        for record in json_list:
            annotation = record[atype]
            if annotation == '':
                continue
            add_to_annotation_collection(annotation_collection, atype, annotation, record['accession'])

    for atype in ['DERS', 'DEEC', 'DEAF', 'CCFU', 'CCLO', 'CCPA', 'CCSI', 'CCSU', 'SPKW', 'CCCO', 'CCCA']:
        annotation_collection[atype] = {}
        for record in json_list:
            annotationlist = record[atype]
            for annotation in annotationlist:
                if annotation == '':
                    continue
                add_to_annotation_collection(annotation_collection, atype, annotation, record['accession'])

    return annotation_collection


def get_consistent_annotations(annotation_collection):
    cutoff = len(annotation_collection['accession_list']) * 0.9
    filtered_annotations = deepcopy(annotation_collection)
    for atype in ['DERF', 'GNNM']:
        for a in annotation_collection[atype]:
            if len(annotation_collection[atype][a]) < cutoff:
                del filtered_annotations[atype][a]

    for atype in ['DERS', 'DEEC', 'DEAF', 'CCFU', 'CCLO', 'CCPA', 'CCSI', 'CCSU', 'SPKW', 'CCCO', 'CCCA']:
        for a in annotation_collection[atype]:
            if len(annotation_collection[atype][a]) < cutoff:
                del filtered_annotations[atype][a]

    return filtered_annotations


def add_to_annotation_collection(annotation_collection, atype, annotation, accession):
    if annotation not in annotation_collection[atype]:
        annotation_collection[atype][annotation] = []
    annotation_collection[atype][annotation].append(accession)


def output_taxonomy_annotation_collection(taxonomy, annotation_collection, outfile=None):
    totalrecords = len(annotation_collection['accession_list'])
    for atype in ['DERF', 'GNNM', 'DERS', 'DEEC', 'DEAF', 'CCFU',
                  'CCLO', 'CCPA', 'CCSI', 'CCSU', 'SPKW', 'CCCO', 'CCCA']:
        if atype in annotation_collection:
            for annotation in annotation_collection[atype]:
                consistentnumber = len(annotation_collection[atype][annotation])
                text = '{0}\t{1}\t{2}\t{3}\t{4}'.format(taxonomy, atype, totalrecords, consistentnumber, annotation)
                if outfile:
                    outfile.write(text + '\n')


# Result is a json object containing several records
# Errors are handled by the get_url_with_retry method
def get_reviewed_uniprot_jsons_from_interpro_id(interpro):
    url = 'https://www.ebi.ac.uk/proteins/api/proteins/InterPro:{0}?offset=0&size=-1&reviewed=true'.format(interpro)
    headers = {"Accept": "application/json"}
    r = utils.get_url_with_retry(url, headers)
    return json.loads(r.text)




