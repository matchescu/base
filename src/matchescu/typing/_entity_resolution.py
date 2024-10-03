from typing import Hashable, Iterable, Sized, Protocol, Callable

from matchescu.typing._data import Record


class EntityReference(Hashable, Record, Protocol):
    pass


class EntityProfile(Iterable[EntityReference], Sized, Protocol):
    """An entity profile is a collection of entity references.

    There are particularities of entity profiles depending on the entity
    resolution model being used:

    * **entity matching**: pairs of entity references
    * **algebraic model**: a non-empty set of entity references
    """


EntityReferenceIdFactory = Callable[[EntityReference], Hashable]
