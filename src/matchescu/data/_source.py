from abc import ABCMeta, abstractmethod
from matchescu.typing import Record


class DataSource(metaclass=ABCMeta):
    def __iter__(self):
        return self

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __next__(self) -> Record:
        pass

    @abstractmethod
    def __getitem__(self, index: int) -> Record:
        pass
