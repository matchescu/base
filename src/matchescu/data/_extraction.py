from typing import Generic, Generator

from matchescu.typing import EntityReference
from matchescu.typing._data import T, DataSource
from matchescu.typing._callable import Trait


class EntityReferenceExtractor(Generic[T]):
    def __init__(self, traits: list[Trait]):
        self.__traits = traits

    def __process_traits(self, item: T) -> Generator[tuple, None, None]:
        for trait in self.__traits:
            trait_result = trait(item)
            if trait_result is None:
                continue
            if isinstance(trait_result, dict):
                yield tuple(trait_result.values())
                continue
            yield trait_result

    def __extract_entity_reference(self, item: T) -> EntityReference:
        return tuple(
            value
            for trait_result in self.__process_traits(item)
            for value in trait_result
        )

    def __call__(self, ds: DataSource[T]) -> Generator[EntityReference, None, None]:
        yield from map(self.__extract_entity_reference, ds)
