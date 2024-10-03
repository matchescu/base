from typing import Any, Callable
from unittest.mock import MagicMock

import pytest

from matchescu.data._extraction import EntityReferenceExtractor


class DataSourceStub(list[int]):
    name: str = "test"


@pytest.mark.parametrize("item_count", [0, 1, 2])
def test_extraction_processes_data_source(item_count):
    mock_trait = MagicMock(spec=Callable[[Any], tuple], return_value=("success",))
    extract = EntityReferenceExtractor([mock_trait])
    source = DataSourceStub(range(item_count))

    references = list(extract(source))

    assert mock_trait.call_count == item_count
    assert references == [("success",)] * item_count


@pytest.mark.parametrize(
    "trait_return_values,expected",
    [
        ([], ()),
        ([("a",)], ("a",)),
        ([("a", "b")], ("a", "b")),
        ([("a",), ("b",)], ("a", "b")),
        ([("a", "b"), ("c",)], ("a", "b", "c")),
        ([("a",), ("b", "c")], ("a", "b", "c")),
    ],
)
def test_extraction_processes_all_traits(trait_return_values, expected):
    traits = [
        MagicMock(
            spec=Callable[[Any], tuple], return_value=ret_val, name=f"trait_{idx+1}"
        )
        for idx, ret_val in enumerate(trait_return_values)
    ]
    extract = EntityReferenceExtractor(traits)
    source = DataSourceStub([0])

    ref = next(extract(source))

    assert all(mock_trait.call_count == 1 for mock_trait in traits)
    assert ref == expected


def test_extraction_skips_over_traits_without_return_value():
    mock_trait = MagicMock(spec=Callable[[Any], tuple], return_value=None)
    extract = EntityReferenceExtractor([mock_trait])
    source = DataSourceStub([0])

    ref = next(extract(source))

    assert ref == ()


def test_extraction_converts_dicts_to_tuples():
    mock_trait = MagicMock(
        spec=Callable[[Any], tuple],
        return_value={
            "k1": "from dict1",
            "k2": "from dict2",
        },
    )
    extract = EntityReferenceExtractor([mock_trait])
    source = DataSourceStub([0])

    ref = next(extract(source))

    assert ref == ("from dict1", "from dict2")
