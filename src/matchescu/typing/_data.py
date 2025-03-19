from collections.abc import Sequence, Iterable
from typing import Sized, Protocol, Union, Any, TypeVar, Callable


class Record(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ for data records.

    A record is information structured using attributes. A record has a length
    (or size), it can be iterated over so that we can browse all of its
    attributes and each attribute may be accessed using a name or an integer
    index.
    """

    data_source: str

    def __getitem__(self, item: Union[str, int]) -> Any:
        """Record values may be accessed by name or index."""


TRecord = TypeVar("TRecord", bound=Record)

Trait = Callable[[Iterable[TRecord]], TRecord]


class DataSource(Iterable[TRecord], Sized, Protocol):
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
    traits: Sequence[Trait]


RecordSampler = Callable[[DataSource], Iterable[TRecord]]
