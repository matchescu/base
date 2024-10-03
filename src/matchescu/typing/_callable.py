from typing import Any, Callable

from matchescu.typing._entity_resolution import EntityReference

Trait = Callable[[Any], tuple]
EntityReferenceIdentifier = Callable[[EntityReference], Any]
