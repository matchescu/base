from typing import Generator, Generic

import networkx as nx

from matchescu.similarity._matcher import Matcher, TRef
from matchescu.similarity._persistence import GraphPersistence
from matchescu.typing._references import EntityReferenceIdentifier


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
    ) -> None:
        self.__directed = directed
        self.__g = nx.DiGraph() if directed else nx.Graph()
        self.__matcher = matcher

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

    def add(self, left: TRef, right: TRef) -> "ReferenceGraph":
        """Add an edge between two entity references.

        The edge is added based on the configured similarity thresholds based
        on the similarity computed by the configured matcher.

        :param left: left entity reference
        :param right: right entity reference

        :return: ``self``, with the added edge.
        """
        sim_score = self.__matcher(left, right)
        self.__g.add_edge(left.id, right.id, weight=sim_score, refs=(left, right))
        return self

    def matches(
        self, match_min: float = 0.75
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from (
            (u, v)
            for u, v, weight in self.__g.edges.data("weight", default=0.0)
            if weight >= match_min
        )

    def potential_matches(
        self, non_match_max: float = 0.25, match_min: float = 0.75
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from (
            (u, v)
            for u, v, weight in self.__g.edges.data("weight", default=0.0)
            if non_match_max <= weight < match_min
        )

    def non_matches(
        self, non_match_max: float = 0.25
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from (
            (u, v)
            for u, v, weight in self.__g.edges.data("weight", default=0.0)
            if weight < non_match_max
        )

    def has_edge(
        self, u: EntityReferenceIdentifier, v: EntityReferenceIdentifier
    ) -> bool:
        return (u, v) in self.__g.edges

    def weight(
        self, left: EntityReferenceIdentifier, right: EntityReferenceIdentifier
    ) -> float:
        data = self.__g.get_edge_data(left, right, default={})
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
        g = self.__g.copy()
        g.add_nodes_from(other.__g.nodes)
        g.add_weighted_edges_from(other.__g.edges(data=True))
        result = ReferenceGraph(self.__matcher, directed=self.__directed)
        result.__g = g
        return result
