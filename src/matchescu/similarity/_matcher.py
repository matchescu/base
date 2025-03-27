from typing import Protocol, TypeVar

from matchescu.typing import EntityReference


TRef = TypeVar("TRef", bound=EntityReference)


class Matcher(Protocol[TRef]):
    @property
    def non_match_threshold(self) -> float:
        """Similarity score (ranged 0..1) below which two references are considered to truly mismatch."""
        pass

    @property
    def match_threshold(self) -> float:
        """Similarity score (ranged 0..1) above which two references are considered to truly match one another."""
        pass

    def __call__(self, left: TRef, right: TRef) -> float:
        """Return a similarity score between ``left`` and ``right``.

        :param left: an entity reference of any kind
        :param right: an entity reference of any kind

        :return: a ``float`` value ranged between 0 and 1 which represents the
            probability that ``left`` matches ``right``.
        """
        raise NotImplementedError()
