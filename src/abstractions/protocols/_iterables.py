from typing import Protocol, Iterable, Sized


class IndexedIterable(Sized, Iterable, Protocol):
    """A `protocol <https://peps.python.org/pep-0544/>`_ that is used throughout the project.

    This protocol specifies that items have the ``__len__``, the ``__iter__`` and the
    ``__getitem__`` attributes.
    """
    def __getitem__(self, item):
        pass
