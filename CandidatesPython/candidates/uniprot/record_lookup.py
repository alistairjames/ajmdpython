import requests
import time
import sys
import json
import logging
logger = logging.getLogger(__name__)


def get_uniprot_url_with_retry(url, headers):
    tries = 1
    r = requests.get(url, headers=headers)
    if r.ok:
        return r
    else:
        while not r.ok and tries < 6:
            tries += 1
            time.sleep(3 ** tries)
            r = requests.get(url, headers=headers)
            if r.ok:
                if tries > 1:
                    logger.warning(f'Took {tries} attempts to collect data from {url}')
                return r
        r.raise_for_status()
        logger.error(f'Failed to collect UniProt record data after {tries} attempts. Giving up analysis.')
        sys.exit()


# Result is a json object containing several records
# Errors are handled by the get_url_with_retry method
def get_reviewed_uniprot_jsons_from_interpro_id(interpro):
    url = 'https://www.ebi.ac.uk/proteins/api/proteins/InterPro:{0}?offset=0&size=-1&reviewed=true'.format(interpro)
    headers = {"Accept": "application/json"}
    r = get_uniprot_url_with_retry(url, headers)
    return json.loads(r.text)


