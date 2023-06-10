from typing import Protocol, Iterable, Sized


class SizedIterable(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ for sized and iterable items."""
