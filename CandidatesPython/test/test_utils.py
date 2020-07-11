import candidates.utils as utils


def test_calculate_thread_count():
    input_data = [1, 5, 9, 11, 20, 200, 500, 740, 760, 10000, 100000]
    results = [utils.calculate_thread_count(n) for n in input_data]
    assert results == [1, 1, 1, 2, 4, 40, 100, 148, 150, 150, 150]


def test_calculate_split_positions():
    list_length = 32
    threads = 4
    results = utils.calculate_split_positions(list_length, threads)
    assert results == [(1, 0, 8), (2, 8, 16), (3, 16, 24), (4, 24, 32)]


