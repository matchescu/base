from typing import Sized, Iterable, Protocol, Union, Any, TypeVar

from matchescu.typing._callable import Trait


T = TypeVar("T")


class Record(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ for data records.

    A record is information structured using attributes. A record has a length
    (or size), it can be iterated over so that we can browse all of its
    attributes and each attribute may be accessed using a name or an integer
    index.
    """

    def __getitem__(self, item: Union[str, int]) -> Any:
        """Record values may be accessed by name or index."""


class DataSource(Iterable[T], Sized, Protocol):
    """A data source is an iterable sequence of relatively similar items.

    Data sources have a size or at least can estimate their own size. Each data
    source has a name.

    Attributes
    ----------
    :name str: name of the data source
    :traits Iterable[Trait]: feature extraction traits that are specific to the
        data source.
    """

    name: str
    traits: Iterable[Trait]
