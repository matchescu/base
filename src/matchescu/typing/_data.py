from typing import Sized, Iterable, Protocol, Union, Any


class Record(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ for records.

    A record is a piece of information that has a structure because of its
    attributes or properties. A record has a length (or size), it can be
    iterated over so that we can browse all of its attributes and each attribute
    may be accessed by its name or by its location.
    """

    def __getitem__(self, item: Union[str, int]) -> Any:
        """Record values may be accessed by name or index."""
