import pytest

from abstractions.data_structures import Table


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
