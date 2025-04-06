import itertools
from enum import StrEnum
from functools import partial
from typing import Generator, Generic

import networkx as nx

from matchescu.similarity._matcher import Matcher, TRef
from matchescu.similarity._persistence import GraphPersistence
from matchescu.typing._references import EntityReferenceIdentifier


class MatchEdgeType(StrEnum):
    MATCH = "match"
    POTENTIAL_MATCH = "potential_match"


class SimilarityGraph(Generic[TRef]):
    def __init__(
        self, matcher: Matcher[TRef], max_non_match: float, min_match: float
    ) -> None:
        self.__g = nx.DiGraph()
        self.__matcher = matcher
        self.__max_bad = max_non_match
        self.__min_good = min_match
        self.__match_count = 0
        self.__potential_match_count = 0
        self.__non_match_count = 0

    def __repr__(self):
        return "SimilarityGraph(nodes={}, edges={}, match={}, non_match={}, maybe={})".format(
            len(self.__g.nodes),
            len(self.__g.edges),
            self.__match_count,
            self.__non_match_count,
            self.__potential_match_count,
        )

    @property
    def nodes(self):
        """Returns the nodes of the graph."""
        return self.__g.nodes

    @property
    def edges(self):
        """Returns the edges of the graph along with their similarity weights and types."""
        return self.__g.edges(data=True)

    @property
    def match_count(self):
        return self.__match_count

    @property
    def potential_match_count(self):
        return self.__potential_match_count

    @property
    def non_match_count(self):
        return self.__non_match_count

    def add(self, left: TRef, right: TRef) -> "SimilarityGraph":
        """Add an edge between two entity references.

        The edge is added based on the configured similarity thresholds based
        on the similarity computed by the configured matcher.

        :param left: left entity reference
        :param right: right entity reference

        :return: ``self``, with the added edge.
        """
        if left not in self.__g:
            self.__g.add_node(left.id)
        if right not in self.__g:
            self.__g.add_node(right.id)

        sim_score = self.__matcher(left, right)
        if sim_score >= self.__min_good:
            self.__g.add_edge(
                left.id, right.id, weight=sim_score, type=MatchEdgeType.MATCH
            )
            self.__match_count += 1
        elif self.__max_bad <= sim_score < self.__min_good:
            self.__g.add_edge(
                left.id, right.id, weight=sim_score, type=MatchEdgeType.POTENTIAL_MATCH
            )
            self.__potential_match_count += 1
        else:
            self.__non_match_count += 1
        return self

    @staticmethod
    def __has_expected_type(edge: tuple, edge_type: MatchEdgeType) -> bool:
        _, __, data = edge
        return data.get("type") == edge_type

    def edges_by_type(
        self, edge_type: MatchEdgeType
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from itertools.starmap(
            lambda a, b, _: (a, b),
            filter(partial(self.__has_expected_type, edge_type=edge_type), self.edges),
        )

    def matches(
        self,
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from self.edges_by_type(MatchEdgeType.MATCH)

    def potential_matches(
        self,
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from self.edges_by_type(MatchEdgeType.POTENTIAL_MATCH)

    def is_match(
        self, left: EntityReferenceIdentifier, right: EntityReferenceIdentifier
    ) -> bool:
        data = self.__g.get_edge_data(left, right, default={})
        return data.get("type") == MatchEdgeType.MATCH

    def is_potential_match(
        self, left: EntityReferenceIdentifier, right: EntityReferenceIdentifier
    ) -> bool:
        data = self.__g.get_edge_data(left, right, default={})
        return data.get("type") == MatchEdgeType.POTENTIAL_MATCH

    def is_non_match(
        self, left: EntityReferenceIdentifier, right: EntityReferenceIdentifier
    ) -> bool:
        return (left, right) not in self.__g.edges

    def weight(
        self, left: EntityReferenceIdentifier, right: EntityReferenceIdentifier
    ) -> float:
        data = self.__g.get_edge_data(left, right, default={})
        return float(data.get("weight", 0.0))

    def load(self, persistence: GraphPersistence) -> "SimilarityGraph":
        g = persistence.load()
        self.__g = nx.DiGraph()
        self.__g.add_nodes_from(g.nodes)
        for u, v, data in g.edges(data=True):
            edge_type = data.get("type", MatchEdgeType.MATCH)
            self.__g.add_edge(
                u,
                v,
                weight=data.get("weight", 1.0),
                type=edge_type,
            )
            if edge_type == MatchEdgeType.MATCH:
                self.__match_count += 1
            elif edge_type == MatchEdgeType.POTENTIAL_MATCH:
                self.__potential_match_count += 1
        return self

    def save(self, persistence: GraphPersistence) -> "SimilarityGraph":
        persistence.save(self.__g)
        return self
