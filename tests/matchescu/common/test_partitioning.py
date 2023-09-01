from matchescu.common.partitioning import compute_partition


def test_reflexivity():
    partition = compute_partition(["a"], {("a", "a")})
    assert len(partition) == 1
    assert partition.pop() == frozenset(["a"])


def test_symmetry():
    partition = compute_partition(["a", "b"], {("a", "b"), ("b", "a")})
    assert len(partition) == 1
    assert partition.pop() == frozenset(["a", "b"])


def test_transitivity():
    partition = compute_partition(
        ["a", "b", "c"],
        {
            ("a", "b"),
            ("b", "c"),
        }
    )

    assert len(partition) == 1
    assert partition.pop() == frozenset(["a", "b", "c"])
