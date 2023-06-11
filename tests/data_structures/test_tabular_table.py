import os

import pytest

from src.abstractions.data_structures import Table


def row_items():
    yield 1362
    yield "amazing book"
    yield "the author"
    yield "a conference venue"
    yield 1998


def row_generator():
    yield row_items()


@pytest.fixture
def row():
    return row_generator()


def test_load_from_iterable(row):
    table = Table("id", "title", "authors", "venue", "year")

    table.load_sequence(row)

    assert table[0]["id"] == 1362
    assert table[0]["title"] == "amazing book"
    assert table[0]["authors"] == "the author"
    assert table[0]["venue"] == "a conference venue"
    assert table[0]["year"] == 1998


def test_load_from_iterable_no_feature_info(row):
    table = Table()

    table.load_sequence(row)

    assert table[0]["column-00001"] == 1362
    assert table[0]["column-00002"] == "amazing book"
    assert table[0]["column-00003"] == "the author"
    assert table[0]["column-00004"] == "a conference venue"
    assert table[0]["column-00005"] == 1998

def test_load_from_csv():
    test_file_path = os.path.join(os.path.dirname(__file__), "test_data.csv")
    result = Table.load_csv(test_file_path)

    assert result.columns[0].name == "a"
    assert result.columns[0].ordinal == 0
    assert result.columns[1].name == "b"
    assert result.columns[1].ordinal == 1
    assert result[0]["a"] == "1"
    assert result[0]["b"] == "2"


def test_sub_table():
    sut = Table("a", "b", "c")
    sut.load_sequence([[1, 2, 3], [4, 5, 6]])

    result = sut.sub_table("a", "c")

    assert result.columns[0].name == "a"
    assert result.columns[0].ordinal == 0
    assert result.columns[1].name == "c"
    assert result.columns[1].ordinal == 1
    assert result[0][0] == 1
    assert result[0][1] == 3
    assert result[1][0] == 4
    assert result[1][1] == 6
