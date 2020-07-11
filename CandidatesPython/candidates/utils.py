from datetime import datetime
import time
import sys
import requests
import logging
logger = logging.getLogger(__name__)


def file_list_to_set(filepath):
    newset = set()
    for line in open(filepath):
        newset.add(line.rstrip())
    return newset


def get_file_lines(filename):
    line_list = []
    with open(filename) as f:
        for line in f:
            line_list.append(line.rstrip())
    return line_list


def get_elapsed_time(start_time) -> str:
    elapsed_time = time.time() - start_time
    return time.strftime("%H:%M:%S", time.gmtime(elapsed_time))


def fileline_filter(filename, text):
    outfile = open(filename + '.filtered.txt', 'w')
    for line in open(filename):
        if text in line:
            outfile.write(line)
    outfile.close()


def get_url_with_retry(url, headers):
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



