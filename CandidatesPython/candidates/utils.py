import time
import requests
import math
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


# Use default thread_id of 1 for methods that run on main thread
# Requests has its own retry system which should really be used here instead
def get_url_with_retry(url, headers, thread_id=1):
    max_tries = 5
    tries = 1
    r = None
    try:
        r = requests.get(url, headers=headers)
    except:
        logger.error('Thread {0}. Try {1}/{2} for {3}'.format(thread_id, tries, max_tries, url))
    if r is not None and r.ok:
        return r
    else:
        while tries <= max_tries:
            tries += 1
            time.sleep(tries * 2)
            try:
                r = requests.get(url, headers=headers)
            except:
                logger.error('Thread {0}. Try {1}/{2} for {3}'.format(thread_id, tries, max_tries, url))
            if r is not None and r.ok:
                return r
    if r is not None:
        r.raise_for_status()
    # Throw an exception if this method failed to access the data
    raise Exception('Thread {0} completely failed to access {1}'.format(thread_id, url))


# Calculate number of threads (t) to use for list length of n
# Use only 1 thread if the list is 10 or less and a maximum of 50 threads
# Requirements:
# if n <= 10,  t = 1
# if n > 250, t = 50
# from 10 to 750 as many threads as possible as long as n/t >= 5
def calculate_thread_count(n: int):
    if n <= 10:
        return 1
    elif n > 250:
        return 50
    else:
        for t in range(50, 1, -1):
            if n / t >= 5:
                return t


# Returns a tuple of 3 integers. The first element of each is used as thread id
# The other two show where to split the list
def calculate_split_positions(list_length: int, threadcount: int) -> list:
    param_list = []
    j = int(math.ceil(list_length / threadcount))
    start, end = 0, 0
    i = 0
    for i in range(threadcount - 1):
        start = i * j
        end = start + j
        param_list.append((i + 1, start, end))
    param_list.append((i + 2, end, list_length))
    return param_list






