import pytest

from matchescu.data._record import Record


@pytest.mark.parametrize(
    "init_data, col_name",
    [
        ({"a"}, "column_1"),
        ({"attr_name": "a"}, "attr_name"),
        (["a"], "column_1"),
        (("a",), "column_1"),
    ],
)
def test_init_from_types_expected_col_name(init_data, col_name):
    r = Record(init_data)
    assert r[col_name] == "a"


@pytest.mark.parametrize("init_data,expected_len", [([], 0), ([1], 1), ([1, 2], 2)])
def test_record_len(init_data, expected_len):
    r = Record(init_data)
    assert len(r) == expected_len


def test_record_iteration():
    r = Record({"a": 1})

    assert list(r) == [1]
