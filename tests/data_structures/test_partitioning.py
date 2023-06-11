import pytest

from abstractions.data_structures import extract_partitions


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ([[1, 2, 3], [4, 5]], [[1, 2, 3], [4, 5]]),
        ([[1, 2, 3], [1, 4]], [[1, 2, 3], [4]]),
        ([[1, 4, 2], [1, 2]], [[1, 4, 2]]),
        ([[1, 2], [1, 2, 3]], [[1, 2], [3]])
    ]
)
def test_extract_partitions(input_data, expected):
    assert list(extract_partitions(input_data)) == expected
