import sys
import os
import os.path
import candidates.interpro as interpro
import candidates.unirule as unirule
import candidates.uniprot.counter as uniprotcounter
import candidates.utils as utils
import candidates.uniprot.collect_candidates as uniprotcollector
from datetime import datetime
import time
import logging
# configure logger as root logger so modules inherit this config with logger = logging.getLogger(__name__)
logger = logging.getLogger()
data_path = os.sep.join(['data', 'main'])


def run_analysis(timestamp, start_time, interpro_path, unirule_path):
    global data_path
    logger.info('Starting main analysis run')

    # Map InterProId to member signatures
    interpro_2_member_path = os.sep.join([data_path, 'output', f'InterProId_MemberId_{timestamp}.tsv'])
    interpro.create_interproid_to_memberid_map(interpro_path, interpro_2_member_path)

    # Map InterProId to InterPro type (Family, Domain, etc)
    interpro_2_type_path = os.sep.join([data_path, 'output', f'InterProId_Type_{timestamp}.tsv'])
    interpro.create_interproid_to_type_map(interpro_path, interpro_2_type_path)

    # Extract InterPro families that do not contain other families as subsets
    interpro_nochild_path = os.sep.join([data_path, 'output', f'InterPro_nochild_nohamap_nopir_{timestamp}.list'])
    interpro.get_family_nochild_interpro(interpro_path, interpro_nochild_path)

    # Extract the list of used signatures from the unifire xml file unirule-urml-latest.xml
    used_signatures_filepath = os.sep.join([data_path, 'output', 'used_signatures_from_urml_file.list'])
    unirule.collect_used_signatures(unirule_path, used_signatures_filepath)

    # Filter the extracted InterPro families to remove any that contain signatures already used in rules
    prelim_candidates_path = os.sep.join([data_path, 'output', f'Prelim_Candidates_{timestamp}.list'])
    interpro.create_interpro_candidate_list(interpro_2_member_path, used_signatures_filepath,
                                            interpro_nochild_path, prelim_candidates_path)

    # Filter the preliminary candidate signatures based on the number of UniProt reviewed and unreviewed hits.
    min_reviewed = 10
    min_unreviewed = 100
    candidates_filtered_path = os.sep.join([data_path, 'output', f'CandidatesFilteredByHits_{timestamp}.tsv'])
    uniprotcounter.collect_counts(prelim_candidates_path, min_reviewed, min_unreviewed, candidates_filtered_path)
    logger.info(f'ElapsedTime: {utils.get_elapsed_time(start_time)}')

    # Look up the reviewed records for the remaining families and collect those with consistent annotation
    outfilepath = os.sep.join([data_path, 'output', f'CandidateRules_{timestamp}.tsv'])
    uniprotcollector.collect_candidates_from_list_with_counts(candidates_filtered_path, outfilepath)
    logger.info(f'Analysis completed. Elapsed time: {utils.get_elapsed_time(start_time)}')


def logger_setup():
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    fh = logging.FileHandler('logs/log.txt', 'w')
    ch.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s:  %(message)s',
                                     datefmt='%y-%m-%d %H:%M:%S')
    ch.setFormatter(log_format)
    fh.setFormatter(log_format)
    logger.addHandler(ch)
    logger.addHandler(fh)


def check_input_data_exists(interpro_path, unirule_path):
    if os.path.isfile(interpro_path) and os.path.isfile(unirule_path):
        logger.info(f'Input data found: {interpro_path} and {unirule_path}')
        return True
    else:
        logger.critical(f'Missing input data: {interpro_path} or {unirule_path}')
        return False


def run_candidates(run_type):
    logger_setup()
    global data_path
    data_path = os.sep.join(['data', run_type])

    # The point for setting the two input file paths
    interpro_xmlpath = os.sep.join([data_path, 'input', 'interpro.xml'])
    unirule_xmlpath = os.sep.join([data_path, 'input', 'unirule-urml-latest.xml'])
    if check_input_data_exists(interpro_xmlpath, unirule_xmlpath):
        timestamp = '{:%Y-%m-%d_%H:%M:%S}'.format(datetime.now())
        start_time = time.time()
        run_analysis(timestamp, start_time, interpro_xmlpath, unirule_xmlpath)
    else:
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'main':
        run_candidates('main')
    else:
        run_candidates('demo')
