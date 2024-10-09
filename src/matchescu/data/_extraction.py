from typing import Generic, Generator, Hashable, Iterable

from matchescu.typing import EntityReference
from matchescu.typing._data import T, DataSource
from matchescu.typing._entity_resolution import EntityReferenceIdFactory


class EntityReferenceExtraction(Generic[T]):
    def __init__(self, ds: DataSource[T], id_factory: EntityReferenceIdFactory):
        self.__ds = ds
        self.__id_factory = id_factory

    def __process_traits(self, item: T) -> Generator[tuple, None, None]:
        for trait in self.__ds.traits:
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

    def identify(self, ref: EntityReference) -> Hashable:
        return self.__id_factory(ref)

    def __call__(self) -> Iterable[EntityReference]:
        return map(self.__extract_entity_reference, self.__ds)
