import itertools
from unittest.mock import call

import pytest


@pytest.mark.parametrize(
    "data_source,expected_length",
    [([{"a": 1}], 1), ([{"a": 1}, (2,)], 2)],
    indirect=["data_source"],
)
def test_reference_extraction_calls_sampler_adapter_and_merger(
    entity_reference_extraction,
    data_source,
    expected_length,
    record_adapter,
    record_sampler,
    record_merge,
):
    references = list(entity_reference_extraction())

    assert len(references) == expected_length
    assert record_sampler.call_count == 1
    assert record_merge.call_count == expected_length
    assert record_adapter.call_count == expected_length


@pytest.mark.parametrize("sample_count", [1, 2])
def test_number_of_references_determined_by_sampler(
    entity_reference_extraction, record_sampler, sample_count
):
    record_sampler.return_value = itertools.repeat(("a", "b"), sample_count)
    references = list(entity_reference_extraction())
    assert len(references) == sample_count


def test_number_of_references_determined_by_merger(
    entity_reference_extraction,
    record_sampler,
    record_merge,
    record_adapter,
    entity_reference,
):
    expected_value = ("merged",)
    # sampler outputs two records at a time
    record_sampler.return_value = [itertools.repeat(("a", "b"), 2)]
    # merger compresses them into a single record
    record_merge.side_effect = lambda _: expected_value

    references = list(entity_reference_extraction())

    assert len(references) == 1
    assert record_adapter.call_args_list == [
        call(expected_value),
    ]
    assert references[0] == entity_reference
