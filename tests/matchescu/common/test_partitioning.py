from matchescu.common.partitioning import compute_partition


def test_reflexivity():
    partition = compute_partition(["a"], [("a", "a")])
    assert len(partition) == 1
    assert partition == [["a"]]


def test_symmetry():
    partition = compute_partition(["a", "b"], [("a", "b"), ("b", "a")])
    assert len(partition) == 1
    assert partition == [["a", "b"]]


def test_transitivity():
    partition = compute_partition(
        ["a", "b", "c"],
        [
            ("a", "b"),
            ("b", "c"),
        ],
    )

    assert len(partition) == 1
    assert partition == [["a", "b", "c"]]


def test_create_single_set():
    partition = compute_partition(
        ["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("d", "a")]
    )

    assert len(partition) == 1
    assert partition == [["a", "b", "c", "d"]]


def test_isolated_item():
    partition = compute_partition(
        ["a", "b", "c", "d"],
        [
            ("a", "b"),
            ("b", "c"),
        ],
    )
    assert len(partition) == 2
    assert partition == [["a", "b", "c"], ["d"]]
