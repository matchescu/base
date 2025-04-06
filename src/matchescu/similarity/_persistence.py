from abc import ABCMeta, abstractmethod

import networkx as nx


class GraphPersistence(metaclass=ABCMeta):
    @abstractmethod
    def load(self) -> nx.Graph:
        pass

    @abstractmethod
    def save(self, g: nx.Graph) -> None:
        pass
