import candidates.utils as utils


def test_calculate_thread_count():
    input_data = [1, 5, 9, 11, 20, 80, 120, 200, 500]
    results = [utils.calculate_thread_count(n) for n in input_data]
    assert results == [1, 1, 1, 2, 4, 16, 24, 40, 50]


def test_calculate_split_positions():
    list_length = 32
    threads = 4
    results = utils.calculate_split_positions(list_length, threads)
    assert results == [(1, 0, 8), (2, 8, 16), (3, 16, 24), (4, 24, 32)]


def test_calculate_split_positions2():
    list_length = 14368
    threads = utils.calculate_thread_count(list_length)
    results = utils.calculate_split_positions(list_length, threads)
    assert results[-2:] == [(49, 13824, 14112), (50, 14112, 14368)]

# This should be mocked really
def test_get_url_with_retry_success():
    success = False
    headers = {"Accept": "text/x-fasta"}
    url = 'https://www.ebi.ac.uk/proteins/api/proteins/InterPro:IPR000068?offset=0&size=1&reviewed=true'
    try:
        result = utils.get_url_with_retry(url, headers)
        success = True
    except:
        pass
    assert success

# Maybe this should be mocked ?
def test_get_url_with_retry_failure():
    failed = False
    headers = {"Accept": "text/x-fasta"}
    url = 'https://localhost:9999'
    try:
        result = utils.get_url_with_retry(url, headers)
    except:
        failed = True
    assert failed
