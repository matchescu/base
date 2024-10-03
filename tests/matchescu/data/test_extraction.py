from typing import Any, Callable
from unittest.mock import MagicMock, call

import pytest

from matchescu.data._extraction import EntityReferenceExtraction
from matchescu.typing import Trait


class DataSourceStub(list[int]):
    name: str = "test"
    traits: list[Trait] = []


@pytest.mark.parametrize("item_count", [0, 1, 2])
def test_extraction_processes_data_source(item_count):
    source = DataSourceStub(range(item_count))
    mock_trait = MagicMock(spec=Callable[[Any], tuple], return_value=("success",))
    source.traits = [mock_trait]
    extract = EntityReferenceExtraction(source, lambda _: 0)

    references = list(extract())

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
    source = DataSourceStub([0])
    source.traits = [
        MagicMock(
            spec=Callable[[Any], tuple], return_value=ret_val, name=f"trait_{idx+1}"
        )
        for idx, ret_val in enumerate(trait_return_values)
    ]
    extract_references = EntityReferenceExtraction(source, lambda _: 0)

    ref = next(iter(extract_references()))

    assert all(mock_trait.call_count == 1 for mock_trait in source.traits)
    assert ref == expected


def test_extraction_skips_over_traits_without_return_value():
    source = DataSourceStub([0])
    mock_trait = MagicMock(spec=Callable[[Any], tuple], return_value=None)
    source.traits = [mock_trait]
    extract_references = EntityReferenceExtraction(source, lambda _: 0)

    ref = next(iter(extract_references()))

    assert ref == ()


def test_extraction_converts_dicts_to_tuples():
    mock_trait = MagicMock(
        spec=Callable[[Any], tuple],
        return_value={
            "k1": "from dict1",
            "k2": "from dict2",
        },
    )
    source = DataSourceStub([0])
    source.traits = [mock_trait]
    extract = EntityReferenceExtraction(source, lambda _: 0)

    ref = next(iter(extract()))

    assert ref == ("from dict1", "from dict2")


def test_extraction_calls_id_factory():
    source = DataSourceStub([0])
    expected = 42
    id_factory_mock = MagicMock(name="id_factory", return_value=expected)
    extract = EntityReferenceExtraction(source, id_factory_mock)

    hashable = next(iter(extract.entity_ids()))

    assert id_factory_mock.call_count == 1
    assert id_factory_mock.call_args_list == [call(0)]
    assert hashable == expected
