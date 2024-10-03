from typing import Callable, Iterable

from matchescu.typing import Record, EntityProfile, EntityReference
from matchescu.data._source import DataSource


Trait = Callable[[Record], tuple]


class EntityReferenceExtractor:
    def __init__(self, traits: list[Trait]):
        self.__traits = traits

    def __extract_entity_reference(self, record: Record) -> EntityReference:
        return tuple(value for trait in self.__traits for value in trait(record))

    def __call__(self, ds: DataSource) -> Iterable[EntityReference]:
        return map(self.__extract_entity_reference, ds)
