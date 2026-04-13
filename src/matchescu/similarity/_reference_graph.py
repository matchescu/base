import itertools
from typing import Generator, Callable, Optional, Self

import networkx as nx

from matchescu.typing._references import EntityReferenceIdentifier as RefId
from ._result import MatchResult
from ._persistence import GraphPersistence


class ReferenceGraph:
    """Graph representation of the similarity between entity references.

    The nodes of the graph are entity reference identifiers. The edges weighted
    on the similarity between nodes. The graph may be directed or undirected.
    By default, it is undirected, suggesting that similarity is symmetric with
    respect to input order, i.e. ``similarity(x, y) == similarity(y, x)``.

    When the graph is directed (i.e., ``similarity(x, y) != similarity(y, x)``),
    the weight of the directed edge from node ``u`` to ``v`` is defined by the
    match probability in that direction, defined as the probability of ``v``
    being a match in the context of ``u`` plus the probability of a symmetric
    match (i.e. the undirected case).
    """

    def __init__(
        self,
        directed: bool = False,
        weight_computer: Optional[Callable[[MatchResult], float]] = None,
    ) -> None:
        self.__directed = directed
        self.__g = nx.DiGraph() if directed else nx.Graph()
        self.__weight_computer = weight_computer or self._compute_weight

    def __repr__(self):
        return "ReferenceGraph(nodes={}, edges={}, directed={})".format(
            len(self.__g.nodes),
            len(self.__g.edges),
            self.__directed,
        )

    @property
    def directed(self):
        return self.__directed

    @property
    def nodes(self):
        """Returns the nodes of the graph."""
        return self.__g.nodes

    @property
    def edges(self):
        """Returns the edges of the graph along with their similarity weights and types."""
        return self.__g.edges(data=True)

    @classmethod
    def _clamp(cls, value: float) -> float:
        return max(min(value, 1.0), 0.0)

    @classmethod
    def _compute_weight(cls, match_result: MatchResult) -> float:
        weight = cls._clamp(match_result.label_weights[match_result.label])
        if match_result.label == 0:
            numerator = 1 - weight
            denominator = len(match_result.label_weights) - 1
            return numerator / denominator
        return weight

    def add(self, result: MatchResult) -> Self:
        """Add an edge between two entity references.

        The edge is added based on the configured similarity thresholds based
        on the similarity computed by the configured matcher.

        :param result: the result of a match operation

        :return: ``self``, with the added edge.
        """
        self.__g.add_node(result.left)
        self.__g.add_node(result.right)
        if result.label == 0:
            return self

        weight = self.__weight_computer(result)
        if self.__directed and len(result.label_weights) > 2:
            match result.label:
                case 1:
                    self.__g.add_edge(
                        result.left, result.right, weight=weight, label=result.label
                    )
                    self.__g.add_edge(
                        result.right, result.left, weight=weight, label=result.label
                    )
                case 2:
                    self.__g.add_edge(
                        result.left, result.right, weight=weight, label=result.label
                    )
        else:  # classic binary matcher (0, 1) -or- not a directed graph
            prev_weight = self.weight(result.left, result.right)
            weight = max(weight, prev_weight)
            self.__g.add_edge(result.left, result.right, weight=weight, label=1)

        return self

    def matches(
        self, min_weight: float = 0.0, max_weight: float = 1.0
    ) -> Generator[tuple[RefId, RefId], None, None]:
        yield from (
            (u, v)
            for u, v, weight in self.__g.edges.data("weight", default=False)
            if min_weight <= weight <= max_weight
        )

    def non_matches(self) -> Generator[tuple[RefId, RefId], None, None]:
        generator = (
            itertools.permutations if self.__directed else itertools.combinations
        )
        yield from (
            (u, v)
            for u, v in generator(self.__g.nodes, 2)
            if not self.__g.has_edge(u, v)
        )

    def has_edge(self, u: RefId, v: RefId) -> bool:
        return self.__g.has_edge(u, v)

    def weight(self, u: RefId, v: RefId) -> float:
        data = self.__g.get_edge_data(u, v, default={})
        return float(data.get("weight", 0.0))

    def label(self, u: RefId, v: RefId) -> int:
        data = self.__g.get_edge_data(u, v, default={})
        return int(data.get("label", 0))

    @classmethod
    def load(cls, persistence: GraphPersistence) -> "ReferenceGraph":
        obj = cls()
        nxg = persistence.load()
        obj.__g = nxg
        obj.__directed = nxg.is_directed()
        return obj

    def save(self, persistence: GraphPersistence) -> "ReferenceGraph":
        persistence.save(self.__g)
        return self

    def to_undirected(self) -> "ReferenceGraph":
        """Convert the graph to an undirected graph.

        If the graph is already undirected, this method returns a copy of the
        graph.
        """
        other = ReferenceGraph(directed=False)
        if self.__directed:
            other.__g.add_edges_from(self.__g.edges(data=True))
        else:
            other.__g = self.__g.copy()
        return other

    def to_directed(self) -> "ReferenceGraph":
        """Convert the graph to a bidirectional directed graph.

        If the graph is already directed, this method returns a copy of the
        graph.
        """
        other = ReferenceGraph(directed=True)
        other.__g = self.__g.copy()
        if not self.__directed:
            for u, v, data in self.__g.edges(data=True):
                other.__g.add_edge(v, u, **data)
        return other

    def merge(self, other: "ReferenceGraph") -> "ReferenceGraph":
        if self.__directed != other.__directed:
            raise ValueError("can't merge directed and undirected graphs")
        g = nx.compose(self.__g, other.__g)
        result = ReferenceGraph(directed=self.__directed)
        result.__g = g
        return result
