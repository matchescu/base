from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic


T = TypeVar("T")


class DataSource(Generic[T], metaclass=ABCMeta):
    def __iter__(self):
        return self

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __next__(self) -> T:
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> T:
        pass
