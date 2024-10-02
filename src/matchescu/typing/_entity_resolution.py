from abc import ABCMeta
from typing import Hashable, Iterable, Sized, Protocol

from matchescu.typing._data import Record


class EntityReference(Hashable, Record):
    pass


class EntityProfile(Iterable[EntityReference], Sized, metaclass=ABCMeta):
    """An entity profile is a collection of entity references.

    There are particularities of entity profiles depending on the entity
    resolution model being used:

    * **entity matching**: pairs of entity references
    * **algebraic model**: a non-empty set of entity references
    """
