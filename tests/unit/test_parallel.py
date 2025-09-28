from annox.io.parallel import map_parallel


def test_map_parallel_ordering():
    data = [1, 2, 3, 4]
    out = map_parallel(lambda x: x * 2, data, workers=0)
    assert [v for _, v in out] == [2, 4, 6, 8]

