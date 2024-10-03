from typing import Sized, Iterable, Protocol, Union, Any


class Record(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ for data records.

    A record is information structured using attributes. A record has a length
    (or size), it can be iterated over so that we can browse all of its
    attributes and each attribute may be accessed using a name or an integer
    index.
    """

    def __getitem__(self, item: Union[str, int]) -> Any:
        """Record values may be accessed by name or index."""
