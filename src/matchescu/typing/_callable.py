from typing import Any, Callable

from matchescu.typing._data import Record
from matchescu.typing._entity_resolution import EntityReference

Trait = Callable[[Record], tuple]
EntityReferenceIdentifier = Callable[[EntityReference], Any]
