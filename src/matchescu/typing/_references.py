from dataclasses import dataclass
from typing import Hashable, Iterable, Sized, Protocol, Callable

from matchescu.typing._data import Record


@dataclass
class EntityReferenceIdentifier:
    label: Hashable
    data_source: str


class EntityReference(Record, Protocol):
    id: EntityReferenceIdentifier


class EntityProfile(Iterable[EntityReference], Sized, Protocol):
    """An entity profile is a collection of entity references.

    There are particularities of entity profiles depending on the entity
    resolution model being used:

    * **entity matching**: pairs of entity references
    * **algebraic model**: a non-empty set of entity references
    """


EntityReferenceIdFactory = Callable[[Record], EntityReferenceIdentifier]
RecordAdapter = Callable[[Record], EntityReference]
