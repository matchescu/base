from collections.abc import Sequence, Iterable
from typing import Sized, Protocol, Union, Any, TypeVar, Callable, Generator


class Record(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ for data records.

    A record is information structured using attributes. A record has a length
    (or size), it can be iterated over so that we can browse all of its
    attributes and each attribute may be accessed using a name or an integer
    index.
    """

    def __getitem__(self, item: Union[str, int]) -> Any:
        """Record values may be accessed by name or index."""


# type variable for generic types that use records
TRecord = TypeVar("TRecord", bound=Record)

# traits take in one or more records and return a single record
Trait = Callable[[Iterable[TRecord]], TRecord]


class DataSource(Iterable[TRecord], Sized, Protocol):
    """A data source is an iterable sequence of relatively similar items.

    Data sources have a size or can at least estimate it. Each data source has a
    name.

    Attributes
    ----------
    :name str: name of the data source
    :traits Sequence[Trait]: entity reference extraction traits specific to this
        data source.
    """

    name: str
    traits: Sequence[Trait]


# Record samplers retrieve a finite number of records at a time from a data source.
RecordSampler = Callable[[DataSource], Generator[list[TRecord], None, None]]
