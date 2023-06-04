import pytest

from abstractions.data_structures import FeatureInfo, Row


def test_row_item_by_existing_name():
    row = Row([FeatureInfo("a", 0)], ["expected"])

    assert row["a"] == "expected"


def test_row_item_by_non_existent_name():
    row = Row([FeatureInfo("a", 0)], ["expected"])

    with pytest.raises(ValueError) as err_proxy:
        assert row["b"]

    assert str(err_proxy.value) == "don't know how to get item b"


def test_row_item_by_misconfigured_name():
    row = Row([FeatureInfo("a", 1)], ["expected"])

    with pytest.raises(ValueError) as err_proxy:
        assert row["a"]

    assert str(err_proxy.value) == "don't know how to get item a"


def test_row_item_by_valid_index():
    row = Row([], ["expected"])

    assert row[0] == "expected"


@pytest.mark.parametrize("out_of_range_index", [-1, 1])
def test_row_item_by_out_of_range_index(out_of_range_index):
    row = Row([], [])

    with pytest.raises(IndexError) as err_proxy:
        assert row[out_of_range_index]

    assert str(err_proxy.value) == "list index out of range"


def test_row_hydrated_iterator():
    row = Row([], ["a"])

    result = next(row)

    assert result == "a"


def test_row_dehydrated_iterator():
    row = Row([], [])

    with pytest.raises(StopIteration):
        next(row)

    assert True


def test_row_set_item_by_name():
    row = Row([FeatureInfo("a", 0)], [0])

    row["a"] = 1

    assert row["a"] == 1


def test_row_set_item_by_unknown_name():
    row = Row([FeatureInfo("a", 0)], [0])

    with pytest.raises(ValueError) as err_proxy:
        row["b"] = 1

    assert str(err_proxy.value) == "don't know how to set item b"


def test_row_set_item_by_misconfigured_name():
    row = Row([FeatureInfo("a", 1)], [0])

    with pytest.raises(ValueError) as err_proxy:
        row["a"] = 1

    assert str(err_proxy.value) == "don't know how to set item a"


def test_row_set_item_by_index():
    row = Row([FeatureInfo("a", 0)], [0])

    row[0] = 1

    assert row[0] == 1
