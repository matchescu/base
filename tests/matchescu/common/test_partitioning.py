import pytest

from matchescu.common.partitioning import compute_partition


@pytest.fixture
def transitive_equivalence():
    return {
        ("a", "b"),
        ("b", "c"),
        ("d", "d"),
    }


def test_partitioning_transitivity(transitive_equivalence):
    partition = compute_partition(
        ["a", "b", "c", "d"],
        transitive_equivalence
    )

    assert len(partition) == 2
    a1_class = list(filter(lambda x: len(x) == 3, partition))
    assert len(a1_class) == 1
    assert a1_class == [{("a1",), ("a2",), ("a3",)}]
    a4_class = list(filter(lambda x: len(x) == 1, partition))
    assert a4_class == [{("a4",)}]
