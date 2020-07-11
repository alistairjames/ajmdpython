"""
Use the proteins API to find out how many reviewed and unreviewed hits there are for each
InterPro id and save the result to a file.  Ask the API to return only one fasta as the number
we want is in the header regardless of how many results are returned.
"""
import concurrent.futures
import candidates.utils as utils
import logging
logger = logging.getLogger(__name__)


def collect_counts_main_thread(input_list: list, min_rev, min_unrev, output_filepath):
    logger.info(f'Collecting reviewed and unreviewed count data from {len(input_list)} InterPro ids'
                ' without using threads')
    outfile = open(output_filepath, 'w')
    count = 0
    for ip in input_list:
        count += 1
        if count % 20 == 0:
            logger.info(f'Collected reviewed and unreviewed counts for {count} signatures')
            outfile.flush()
        reviewedcount = get_count(ip, True)
        if reviewedcount >= min_rev:
            unreviewedcount = get_count(ip, False)
            if unreviewedcount >= min_unrev:
                outfile.write('{0}\t{1}\t{2}\n'.format(ip, reviewedcount, unreviewedcount))
    logger.info(f'Collected reviewed and unreviewed counts for {count} signatures')
    outfile.close()


# First get all the reviewed data and then all the unreviewed data for those that pass min_rev
def collect_counts(input_list_path, min_rev, min_unrev, output_filepath):
    interpro_list = utils.get_file_lines(input_list_path)

    # Calculate thread count for reviewed hits collection only
    thread_count = utils.calculate_thread_count(len(interpro_list))
    if thread_count == 1:
        collect_counts_main_thread(interpro_list, min_rev, min_unrev, output_filepath)
        return
    else:
        logger.info(f'Collecting reviewed hits from {len(interpro_list)} InterPro ids using {thread_count} threads')

    # Get reviewed hit counts (Get hit counts needs a string true / false not a boolean
    parameters = get_hitcount_parameters_for_executor_map(thread_count, interpro_list, True)
    reviewed_results_dict = get_hit_counts_with_threads(parameters)
    filtered_interpro_list = [x for x in reviewed_results_dict if reviewed_results_dict[x] >= 10]

    # Recalcuculate the threads needed for this list and set the parameters for collecting unreviewed data
    thread_count = utils.calculate_thread_count(len(filtered_interpro_list))
    logger.info(f'Collecting unreviewed hits from {len(interpro_list)} InterPro ids using {thread_count} threads')
    parameters = get_hitcount_parameters_for_executor_map(thread_count, filtered_interpro_list, False)
    unreviewed_results_dict = get_hit_counts_with_threads(parameters)

    filtered_unreviewed_list = [x for x in unreviewed_results_dict if unreviewed_results_dict[x] >= 100]

    final_interpro_hits_list = []
    for ipr in filtered_unreviewed_list:
        final_interpro_hits_list.append((ipr, reviewed_results_dict[ipr], unreviewed_results_dict[ipr]))

    # gather the data temp data together and write to file
    outfile = open(output_filepath, 'w')
    for t in final_interpro_hits_list:
        outfile.write('{0}\t{1}\t{2}\n'.format(t[0], t[1], t[2]))
    outfile.close()
    logger.info(f'Collected reviewed and unreviewed counts for {len(final_interpro_hits_list)} '
                f'signatures using {thread_count} threads')


def get_hitcount_parameters_for_executor_map(threads: int, id_list: list, reviewed: bool) -> list:
    parameter_list = []
    for split in utils.calculate_split_positions(len(id_list), threads):
        thread_id, start, end = split
        parameter_list.append((thread_id, id_list[start:end], reviewed))
    return parameter_list


def get_hit_counts_with_threads(params: list) -> dict:
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(params)) as executor:
        results = executor.map(collect_batch_of_hit_counts, params)
        # This is a list of dictionaries
        all_results = list(results)
    # Merge the results
    all_results_dict = all_results[0]
    for i in range(1, len(all_results)):
        all_results_dict.update(all_results[i])

    return all_results_dict


def collect_batch_of_hit_counts(params: tuple) -> dict:
    thread_id, id_list, reviewed = params
    result_dict = {}
    logger.info(f'Thread {thread_id} has started collecting {len(id_list)} {reviewed} items')
    count = 0
    for ipr in id_list:
        count += 1
        if count % 5 == 0:
            logger.info(f'Thread {thread_id} has collected {count} out of {len(id_list)} {reviewed} items')
        result_dict[ipr] = get_count(ipr, reviewed)
    return result_dict


def get_count(ip: str, isreviewed: bool):
    baseurl = 'https://www.ebi.ac.uk/proteins/api/proteins/InterPro:{0}?offset=0&size=1&reviewed='.format(ip)
    if isreviewed:
        url = baseurl + 'true'
    else:
        url = baseurl + 'false'
    headers = {"Accept": "text/x-fasta"}
    r = utils.get_url_with_retry(url, headers)
    return int(r.headers['x-pagination-totalrecords'])
