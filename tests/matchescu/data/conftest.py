from typing import Iterable, Callable, cast
from unittest.mock import MagicMock

import pytest

from matchescu.data import EntityReferenceExtraction
from matchescu.typing import (
    Trait,
    RecordAdapter,
    RecordSampler,
    Record,
    EntityReference,
    EntityReferenceIdentifier,
)


class DataSourceStub(list[int]):
    name: str = "test"
    traits: list[Trait] = []


@pytest.fixture
def entity_reference(data_source) -> EntityReference:
    mock = MagicMock(name="EntityReferenceMock", spec=EntityReference)
    mock.id = EntityReferenceIdentifier(label=1, source=data_source.name)
    return cast(EntityReference, mock)


@pytest.fixture
def data_source(request) -> DataSourceStub:
    return (
        DataSourceStub(request.param)
        if hasattr(request, "param")
        and isinstance(request.param, Iterable)
        and request.param
        else DataSourceStub()
    )


@pytest.fixture
def record_sampler(data_source) -> RecordSampler:
    mock = MagicMock(name="RecordSamplerMock", spec=RecordSampler)
    mock.return_value = [[item] for item in data_source]
    return mock


@pytest.fixture
def record_merge(request) -> Callable[[Iterable[Record]], Record]:
    mock = MagicMock(name="RecordMergeMock", spec=Callable[[Iterable[Record]], Record])
    if hasattr(request, "param"):
        if isinstance(request.param, int):
            mock.return_value = tuple(range(request.param))
        else:
            mock.return_value = request.param
    else:
        mock.side_effect = lambda r: tuple(value for record in r for value in record)
    return mock


@pytest.fixture
def record_adapter(entity_reference, record_merge) -> RecordAdapter:
    mock = MagicMock(name="RecordAdapterMock", spec=RecordAdapter)
    mock.return_value = entity_reference
    return mock


class EntityReferenceExtractionStub(EntityReferenceExtraction):
    def __init__(
        self,
        ds: DataSourceStub,
        record_adapter: RecordAdapter,
        record_sampler: RecordSampler,
        record_merge: Callable[[Iterable[Record]], Record],
    ):
        super().__init__(ds, record_adapter, record_sampler)
        self.__record_merge = record_merge

    def _merge_records(self, records: Iterable[Record]) -> Record:
        return self.__record_merge(records)


@pytest.fixture
def entity_reference_extraction(
    data_source, record_adapter, record_sampler, record_merge
):
    return EntityReferenceExtractionStub(
        data_source, record_adapter, record_sampler, record_merge
    )
