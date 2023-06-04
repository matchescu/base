from abstractions.data_structures import Table, Clustering


def test_basic_input():
    t1 = Table("a", "b")
    t1.load_sequence([[1, 2], [3, 4]])
    t2 = Table("c", "d")
    t2.load_sequence([[5, 6], [7, 8]])

    result = Clustering.from_tables(t1, t2)

    actual = list(tuple(x.name for x in feature) for feature in result.feature_info)
    assert actual == [("a", "b"), ("c", "d")]
    assert result.clustered_rows == [
        ((1, 2), (5, 6)),
        ((3, 4), (7, 8)),
    ]
