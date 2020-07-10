"""
Use the proteins API to find out how many reviewed and unreviewed hits there are for each
InterPro id and save the result to a file.  Ask the API to return only one fasta as the number
we want is in the header regardless of how many results are returned.
"""

import requests
import sys
import time
import candidates.utils as utils
import logging
logger = logging.getLogger(__name__)


def get_count(ip, isreviewed):
    baseurl = 'https://www.ebi.ac.uk/proteins/api/proteins/InterPro:{0}?offset=0&size=1&reviewed='.format(ip)
    return get_hit_numbers(baseurl + isreviewed)

# ------- Make the normal method in record_lookup ---------------
def get_hit_numbers(url):
    headers = 'headers={"Accept" : "text/x-fasta"}'
    tries = 1
    r = requests.get(url, headers)
    if r.ok:
        return int(r.headers['x-pagination-totalrecords'])
    else:
        while not r.ok and tries < 6:
            tries += 1
            time.sleep(3 ** tries)
            r = requests.get(url, headers)
            if r.ok:
                if tries > 1:
                    logger.warning(f'Took {tries} attempts to collect data from {url}')
                return int(r.headers['x-pagination-totalrecords'])
        r.raise_for_status()
        logger.error(f'Failed to collect UniProt record data after {tries} attempts. Giving up analysis.')
        sys.exit()


def collect_counts(input_list_path, min_rev, min_unrev, output_filepath):
    interpro_list = utils.get_file_lines(input_list_path)
    logger.info(f'Collecting reviewed and unreviewed count data from {len(interpro_list)} InterPro ids')
    outfile = open(output_filepath, 'w')
    count = 0
    for ip in interpro_list:
        count += 1
        if count % 20 == 0:
            logger.info(f'Collected reviewed and unreviewed counts for {count} signatures')
            outfile.flush()
        reviewedcount = get_count(ip, 'true')
        unreviewedcount = get_count(ip, 'false')
        if reviewedcount >= min_rev and unreviewedcount >= min_unrev:
            outfile.write('{0}\t{1}\t{2}\n'.format(ip, reviewedcount, unreviewedcount))
    logger.info(f'Collected reviewed and unreviewed counts for {count} signatures')
    outfile.close()

