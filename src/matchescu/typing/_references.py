from dataclasses import dataclass
from typing import Hashable, Iterable, Sized, Protocol, Callable, Any

from matchescu.typing._data import Record


@dataclass(frozen=True, eq=True)
class EntityReferenceIdentifier:
    """Identifies an entity reference.

    Attributes:
        :label Hashable: unique label identifying an entity reference within a collection
        :source str: a string describing where the entity reference originated
    """

    label: Hashable
    source: str


class EntityReference(Record, Protocol):
    """An entity reference instance allows accessing data by name or index.

    Attributes:
        :id EntityReferenceIdentifier: identifies the entity reference
    """

    id: EntityReferenceIdentifier

    def as_dict(self) -> dict[str, Any]:
        """Return a dictionary containing the reference's attribute names and values."""
        pass


class EntityProfile(Iterable[EntityReference], Sized, Protocol):
    """Entity profiles are iterable sequences of a finite number of entity
    references.

    Concrete entity profiles have different representations according to the
    entity resolution model being used.
    """


EntityReferenceIdFactory = Callable[[Record], EntityReferenceIdentifier]
RecordAdapter = Callable[[Record], EntityReference]
