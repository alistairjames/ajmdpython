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


# Calculate number of threads (t) to use for list length of n
# Requirements:
# if n <= 10,  t = 1
# if n > 750, t = 150
# from 10 to 750 as many threads as possible as long as n/t >= 5
def calculate_thread_count(n: int):
    if n <= 10:
        return 1
    elif n > 750:
        return 150
    else:
        for t in range(150, 1, -1):
            if n / t >= 5:
                return t


# Returns a tuple of 3 integers. The first element of each is used as thread id
# The other two show where to split the list
def calculate_split_positions(list_length: int, threadcount: int) -> list:
    param_list = []
    j = int(list_length / threadcount)
    start, end = 0, 0
    i = 0
    for i in range(threadcount - 1):
        start = i * j
        end = start + j
        param_list.append((i + 1, start, end))
    param_list.append((i + 2, end, list_length))
    return param_list






