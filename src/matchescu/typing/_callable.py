from typing import Protocol, Any

from matchescu.typing._entity_resolution import EntityReference


class EntityReferenceIdentifier(Protocol):
    """Get the identifying information from an entity reference."""
    def __call__(self, ref: EntityReference) -> Any:
        """Retrieves the information that makes ref unique in a context.

        :param ref: an entity reference constructed from a data source

        :return: the information that identifies the entity reference within
        the data extraction process.
        """
        pass
