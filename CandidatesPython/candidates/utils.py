from datetime import datetime
import time
import sys


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




