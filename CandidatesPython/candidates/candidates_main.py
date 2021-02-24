import sys
import os
import os.path
import candidates.interpro as interpro
import candidates.unirule as unirule
import candidates.uniprot.count_candidate_hits as uniprotcounter
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
    interpro_2_member_path = os.sep.join([data_path, 'output', 'InterProId_MemberId_{0}.tsv'.format(timestamp)])
    interpro.create_interproid_to_memberid_map(interpro_path, interpro_2_member_path)

    # Map InterProId to InterPro type (Family, Domain, etc)
    interpro_2_type_path = os.sep.join([data_path, 'output', 'InterProId_Type_{0}.tsv'.format(timestamp)])
    interpro.create_interproid_to_type_map(interpro_path, interpro_2_type_path)

    # Extract InterPro families that do not contain other families as subsets
    interpro_nochild_path = os.sep.join([data_path, 'output', 'InterPro_nochild_nohamap_nopir_{0}.list'.format(timestamp)])
    interpro.get_family_nochild_interpro(interpro_path, interpro_nochild_path)

    # Extract the list of used signatures from the unifire xml file unirule-urml-latest.xml
    used_signatures_outpath = os.sep.join([data_path, 'output', 'used_signatures_from_urml_file.list'])
    unirule.collect_used_signatures(unirule_path, used_signatures_outpath)

    # Filter the extracted InterPro families to remove any that contain signatures already used in rules
    prelim_candidates_path = os.sep.join([data_path, 'output', 'Prelim_Candidates_{0}.list'.format(timestamp)])
    interpro.create_interpro_candidate_list(interpro_2_member_path, used_signatures_outpath,
                                            interpro_nochild_path, prelim_candidates_path)

    # Filter the preliminary candidate signatures based on the number of UniProt reviewed and unreviewed hits.
    min_reviewed = 10
    min_unreviewed = 100
    candidates_filtered_path = os.sep.join([data_path, 'output', 'CandidatesFilteredByHits_{0}.tsv'.format(timestamp)])
    uniprotcounter.collect_counts(prelim_candidates_path, min_reviewed, min_unreviewed, candidates_filtered_path)
    logger.info('ElapsedTime: ' + utils.get_elapsed_time(start_time))

    # Look up the reviewed records for the remaining families and collect those with consistent annotation
    outfile_path = os.sep.join([data_path, 'output', 'CandidateRules_{0}.tsv'.format(timestamp)])
    uniprotcollector.collect_candidates_with_threads(candidates_filtered_path, outfile_path)
    logger.info('Analysis completed. Elapsed time: ' + utils.get_elapsed_time(start_time))
    logger.info('Intermediate and final data saved to: {0}/{1}/output/'.format(os.getcwd(), data_path))
    logger.info('Final data for candidates is in file: CandidateRules_{0}.tsv'.format(timestamp))


def logger_setup(timestamp):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logpath = os.sep.join(['logs', 'log_{0}.txt'.format(timestamp)])
    fh = logging.FileHandler(logpath, 'w')
    ch.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s:  %(message)s',
                                     datefmt='%y-%m-%d %H:%M:%S')
    ch.setFormatter(log_format)
    fh.setFormatter(log_format)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info('File path for the log is ' + logpath)


def check_input_data_exists(interpro_path, unirule_path):
    if os.path.isfile(interpro_path) and os.path.isfile(unirule_path):
        logger.info('Input data found: {0} and {1}'.format(interpro_path, unirule_path))
        return True
    else:
        logger.critical('Missing input data: {0} or {1}'.format(interpro_path, unirule_path))
        return False


def run_candidates(run_type):
    timestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.now())
    logger_setup(timestamp)
    global data_path
    data_path = os.sep.join(['data', run_type])

    # The point for setting the two input file paths
    interpro_xmlpath = os.sep.join([data_path, 'input', 'interpro.xml'])
    unirule_xmlpath = os.sep.join([data_path, 'input', 'unirule-urml-latest.xml'])
    if check_input_data_exists(interpro_xmlpath, unirule_xmlpath):
        start_time = time.time()
        run_analysis(timestamp, start_time, interpro_xmlpath, unirule_xmlpath)
    else:
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'main':
        run_candidates('main')
    else:
        run_candidates('demo')
