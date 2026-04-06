import itertools
from typing import Generator, Generic, Callable, Optional

import networkx as nx

from matchescu.typing._references import EntityReferenceIdentifier
from ._matcher import Matcher, TRef
from ._result import MatchResult
from ._persistence import GraphPersistence


class ReferenceGraph(Generic[TRef]):
    """Graph representation of the similarity between entity references.

    The nodes of the graph are entity references that were compared against each
    other when the ``add`` method was called. Edges in this graph are weighted
    using the matcher passed to the constructor.

    Reference graphs may be directed or undirected. By default, they are
    undirected, suggesting that the matcher is symmetric,
    i.e. ``matcher(x, y) == matcher(y, x)``.
    """

    def __init__(
        self,
        matcher: Matcher[TRef],
        directed: bool = False,
        weight_computer: Optional[Callable[[MatchResult], float]] = None,
    ) -> None:
        self.__directed = directed
        self.__g = nx.DiGraph() if directed else nx.Graph()
        self.__matcher = matcher
        self.__weight_computer = weight_computer or self._compute_weight

    def __repr__(self):
        return "SimilarityGraph(nodes={}, edges={}, matcher={})".format(
            len(self.__g.nodes),
            len(self.__g.edges),
            repr(self.__matcher),
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

    @staticmethod
    def _compute_weight(match_result: MatchResult) -> float:
        if match_result.label == 0:
            numerator = 1 - match_result.label_weights[match_result.label]
            denominator = len(match_result.label_weights) - 1
            return numerator / denominator
        return match_result.label_weights[match_result.label]

    def add(self, left: TRef, right: TRef) -> "ReferenceGraph":
        """Add an edge between two entity references.

        The edge is added based on the configured similarity thresholds based
        on the similarity computed by the configured matcher.

        :param left: left entity reference
        :param right: right entity reference

        :return: ``self``, with the added edge.
        """
        match_result = self.__matcher(left, right)
        self.__g.add_node(left.id)
        self.__g.add_node(right.id)
        if match_result.label == 0:
            return self

        weight = self.__weight_computer(match_result)
        if self.__directed and len(match_result.label_weights) > 2:
            match match_result.label:
                case 1:
                    self.__g.add_edge(
                        left.id, right.id, weight=weight, refs=(left, right)
                    )
                    self.__g.add_edge(
                        right.id, left.id, weight=weight, refs=(right, left)
                    )
                case 2:
                    self.__g.add_edge(
                        left.id, right.id, weight=weight, refs=(left, right)
                    )
                case 3:
                    self.__g.add_edge(
                        right.id, left.id, weight=weight, refs=(right, left)
                    )
        else:  # classical, binary matcher (0, 1)
            self.__g.add_edge(
                left.id,
                right.id,
                weight=weight,
                refs=(left, right),
            )

        return self

    def matches(
        self, min_weight: float = 0.5
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from (
            (u, v)
            for u, v, weight in self.__g.edges.data("weight", default=False)
            if weight >= min_weight
        )

    def potential_matches(
        self, min_weight: float = 0.25, max_weight: float = 0.75
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from (
            (u, v)
            for u, v, weight in self.__g.edges.data("weight", default=0.0)
            if min_weight <= weight < max_weight
        )

    def non_matches(
        self,
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        generator = (
            itertools.permutations if self.__directed else itertools.combinations
        )
        yield from (
            (u, v)
            for u, v in generator(self.__g.nodes, 2)
            if not self.__g.has_edge(u, v)
        )

    def has_edge(
        self, u: EntityReferenceIdentifier, v: EntityReferenceIdentifier
    ) -> bool:
        return self.__g.has_edge(u, v)

    def weight(
        self, u: EntityReferenceIdentifier, v: EntityReferenceIdentifier
    ) -> float:
        data = self.__g.get_edge_data(u, v, default={})
        return float(data.get("weight", 0.0))

    def load(self, persistence: GraphPersistence) -> "ReferenceGraph":
        self.__g = persistence.load()
        self.__directed = self.__g.is_directed()
        return self

    def save(self, persistence: GraphPersistence) -> "ReferenceGraph":
        persistence.save(self.__g)
        return self

    def to_undirected(self) -> "ReferenceGraph":
        """Convert the graph to an undirected graph.

        If the graph is already undirected, this method returns a copy of the
        graph.
        """
        other = ReferenceGraph(self.__matcher, directed=False)
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
        other = ReferenceGraph(self.__matcher, directed=True)
        if self.__directed:
            other.__g = self.__g.copy()
        else:
            for _, __, (u, v) in self.__g.edges.data("refs", default=0.0):
                other.add(u, v)
                other.add(v, u)
        return other

    def merge(self, other: "ReferenceGraph") -> "ReferenceGraph":
        if self.__matcher != other.__matcher:
            raise ValueError("Cannot merge graphs with different matchers.")
        if self.__directed != other.__directed:
            raise ValueError("Cannot merge graphs with different directions.")
        g = nx.compose(self.__g, other.__g)
        result = ReferenceGraph(self.__matcher, directed=self.__directed)
        result.__g = g
        return result
