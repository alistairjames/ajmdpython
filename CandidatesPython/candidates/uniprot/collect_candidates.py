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
import concurrent.futures
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


def collect_candidates_on_main_thread(signature_with_counts_list: list, outfilepath: str):
    n = len(signature_with_counts_list)
    logger.info(f'Starting to collect candidate rules from {n} InterPro signatures on main thread')

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
            get_taxonomy_annotation_collection(taxon, consistent_annotations, outfile)

    outfile.close()
    logger.info(f'Data collected for {count} candidate signatures')


def collect_candidates_with_threads(infile_path: str, outfile_path: str):
    sig_with_counts_strings = [line.rstrip() for line in open(infile_path)]
    list_length = len(sig_with_counts_strings)
    thread_count = utils.calculate_thread_count(len(sig_with_counts_strings))
    if thread_count == 1:
        collect_candidates_on_main_thread(sig_with_counts_strings, outfile_path)
        return
    else:
        logger.info(f'Collecting data for {list_length} InterPro candidates using {thread_count} threads')

    params = get_candidate_parameters_for_executor_map(thread_count, sig_with_counts_strings)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(params)) as executor:
        results = executor.map(collect_batch_of_candidates, params)
        # Candidate is returned from each thread as a dictionary ipr: candidate_text_lines
        # all_results is a list of dictionaries
        all_results = list(results)
    # Merge the results
    all_results_dict = all_results[0]
    for i in range(1, len(all_results)):
        all_results_dict.update(all_results[i])

    outfile = open(outfile_path, 'w')
    outfile.write('# Columns: TaxonomicGroup / AnnotationCode / Total / Consistent / AnnotationText\n')
    # IPR000030  Reviewed: 96  Unreviewed: 13114

    # May as well sort on the keys!
    for key in sorted(all_results_dict):
        interpro, reviewed, unreviewed = key.split('\t')
        text = f'\n# {interpro}  Reviewed:  {reviewed}  Unreviewed:  {unreviewed}\n'
        outfile.write(text)
        outfile.write('\n'.join(all_results_dict[key]) + '\n')
    outfile.close()
    logger.info(f'Collected candidate data for {len(all_results_dict)} candidate signatures')


# string_list is list of (InterProId \t rev \t unrev)
def get_candidate_parameters_for_executor_map(threads: int, string_list: list) -> list:
    parameter_list = []
    for split in utils.calculate_split_positions(len(string_list), threads):
        thread_id, start, end = split
        parameter_list.append((thread_id, string_list[start:end]))
    return parameter_list


# input_data is thread_id, and list of strings Interpro_id \t reviewed_count \t unreviewed_count
def collect_batch_of_candidates(input_data: tuple) -> dict:
    thread_id, interpro_data_list = input_data
    if thread_id == 1:
        logger.info(f'Thread {thread_id} has started collecting {len(interpro_data_list)} candidates')
    result_dict = {}
    count = 0
    for data in interpro_data_list:
        signature, reviewed, unreviewed = data.split('\t')
        count += 1
        if thread_id == 1 and count % 5 == 0:
            logger.info(f'Thread {thread_id} collected data for {count} candidate signatures')
        # this gets a single json object containing several uniprot records
        jsonrecords = get_reviewed_uniprot_jsons_from_interpro_id(signature, thread_id)
        # update the reviewed count in case there is an update in the database
        reviewed = len(jsonrecords)
        updated_key = f'{signature}\t{reviewed}\t{unreviewed}'
        all_tax_data = []
        taxonomy_groups = group_records_by_taxonomy_from_json(jsonrecords)
        for taxon in taxonomy_groups:
            annotation_collection = get_json_data_grouped_by_annotations(taxonomy_groups[taxon])
            consistent_annotations = get_consistent_annotations(annotation_collection)
            candidate_data = get_taxonomy_annotation_collection(taxon, consistent_annotations)
            all_tax_data.extend(candidate_data)
        result_dict[updated_key] = all_tax_data
    if thread_id == 1:
        logger.info(f'Thread {thread_id} has finished collecting data for {count} candidates '
                                                           f'out of {len(interpro_data_list)}')
    return result_dict


# Result is a json object containing several records
# Errors are handled by the get_url_with_retry method
# Default thread_id of 1 in case called on main thread
def get_reviewed_uniprot_jsons_from_interpro_id(interpro: str, thread_id=1) -> json:
    url = 'https://www.ebi.ac.uk/proteins/api/proteins/InterPro:{0}?offset=0&size=-1&reviewed=true'.format(interpro)
    headers = {"Accept": "application/json"}
    try:
        r = utils.get_url_with_retry(url, headers, thread_id)
    except Exception as e:
        logger.error(str(e))
        logger.error('Giving up analysis.')
        sys.exit(0)
    return json.loads(r.text)


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


def get_json_data_grouped_by_annotations(json_list) -> dict:
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


def get_consistent_annotations(annotation_collection) -> dict:
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


# Collects for one taxonomy which will be only part of the data for one InterPro Id
def get_taxonomy_annotation_collection(taxonomy, consistent_annotation, outfile=None):
    totalrecords = len(consistent_annotation['accession_list'])
    text_data = []
    for atype in ['DERF', 'GNNM', 'DERS', 'DEEC', 'DEAF', 'CCFU',
                  'CCLO', 'CCPA', 'CCSI', 'CCSU', 'SPKW', 'CCCO', 'CCCA']:
        if atype in consistent_annotation:
            for annotation in consistent_annotation[atype]:
                consistentnumber = len(consistent_annotation[atype][annotation])
                text = '{0}\t{1}\t{2}\t{3}\t{4}'.format(taxonomy, atype, totalrecords, consistentnumber, annotation)
                text_data.append(text)
                if outfile:
                    outfile.write(text + '\n')
    return text_data





