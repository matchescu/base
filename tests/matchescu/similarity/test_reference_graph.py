from math import isclose
from unittest.mock import MagicMock

import networkx as nx
import pytest

from matchescu.similarity import MatchResult
from matchescu.similarity._persistence import GraphPersistence
from matchescu.similarity._reference_graph import ReferenceGraph


@pytest.fixture
def persistence():
    return MagicMock(spec=GraphPersistence)


@pytest.fixture(scope="module")
def comparison_space(ref):
    return {(ref(1, "a"), ref(1, "b")), (ref(1, "b"), ref(1, "a"))}


@pytest.fixture
def comparison(ref_id):
    return ref_id(1, "a"), ref_id(1, "b")


@pytest.fixture
def is_match(request):
    return getattr(request, "param", True)


@pytest.fixture
def match_prediction(ref_id, request, comparison):
    left, right = getattr(request, "param", comparison)
    return MatchResult(left, right, 1, [0, 1])


@pytest.fixture
def non_match_prediction(ref_id, request, comparison):
    left, right = getattr(request, "param", comparison)
    return MatchResult(left, right, 0, [1, 0])


@pytest.fixture
def is_directed(request):
    return bool(getattr(request, "param", True))


@pytest.fixture
def reference_graph(is_directed):
    return ReferenceGraph(directed=is_directed)


@pytest.mark.parametrize(
    "is_directed,expected_matches",
    [(True, 2), (False, 1)],
    indirect=["is_directed"],
)
def test_add_match_edge(comparison, reference_graph, is_directed, expected_matches):
    left, right = comparison

    reference_graph.add(MatchResult(left, right, 1, [0, 1]))
    reference_graph.add(MatchResult(right, left, 1, [0, 1]))

    matches = list(reference_graph.matches())
    assert len(matches) == expected_matches


@pytest.mark.parametrize(
    "min_weight,max_weight,expected", [(0.51, 1.0, 0), (0.0, 0.49, 0), (0.49, 0.51, 1)]
)
def test_match_filtering(reference_graph, ref_id, min_weight, max_weight, expected):
    reference_graph.add(MatchResult(ref_id(1, "a"), ref_id(1, "b"), 1, [0.5, 0.5]))

    matches = list(reference_graph.matches(min_weight, max_weight))

    assert len(matches) == expected


@pytest.mark.parametrize(
    "is_directed,expected_non_matches",
    [(True, 2), (False, 1)],
    indirect=["is_directed"],
)
def test_add_non_match(comparison, reference_graph, is_directed, expected_non_matches):
    left, right = comparison
    reference_graph.add(MatchResult(left, right, 0, [1, 0]))
    reference_graph.add(MatchResult(right, left, 0, [1, 0]))

    non_matches = list(reference_graph.non_matches())

    assert len(non_matches) == expected_non_matches


@pytest.mark.parametrize(
    "is_directed,expected",
    [(False, True), (True, False)],
    indirect=["is_directed"],
)
def test_has_edge_directed(reference_graph, ref, is_directed, expected, comparison):
    left, right = comparison
    result = MatchResult(left, right, 1, [0, 1])

    reference_graph.add(result)

    assert reference_graph.has_edge(right, left) == expected


@pytest.mark.parametrize("label,weights", [(1, [0, 1]), (0, [1, 0])])
def test_has_edge_is_match(reference_graph, ref, comparison, label, weights):
    left, right = comparison

    reference_graph.add(MatchResult(left, right, label, weights))

    has_edge = reference_graph.has_edge(left, right)
    is_match = label != 0
    assert has_edge == is_match


def test_weight_directed(reference_graph, comparison):
    left, right = comparison
    fwd_result = MatchResult(left, right, 1, [0.4, 0.6])
    rev_result = MatchResult(right, left, 1, [0.3, 0.7])

    reference_graph.add(fwd_result)
    reference_graph.add(rev_result)

    assert reference_graph.weight(left, right) == 0.6
    assert reference_graph.weight(right, left) == 0.7


@pytest.mark.parametrize(
    "fwd,rev,expected_fwd,expected_rev,is_directed",
    [
        (0.6, 0.7, 0.6, 0.7, True),
        (0.7, 0.6, 0.7, 0.6, True),
        (0.6, 0.7, 0.7, 0.7, False),
        (0.7, 0.6, 0.7, 0.7, False),
    ],
    indirect=["is_directed"],
)
def test_weight_undirected_is_always_highest_weight(
    is_directed, reference_graph, comparison, fwd, rev, expected_fwd, expected_rev
):
    left, right = comparison
    fwd_result = MatchResult(left, right, 1, [1 - fwd, fwd])
    rev_result = MatchResult(right, left, 1, [1 - rev, rev])

    reference_graph.add(fwd_result)
    reference_graph.add(rev_result)

    assert reference_graph.weight(left, right) == expected_fwd
    assert reference_graph.weight(right, left) == expected_rev


def test_save(reference_graph, ref, persistence, match_prediction):
    reference_graph.add(match_prediction)

    reference_graph.save(persistence)

    assert persistence.save.call_count == 1
    actual_graph = persistence.save.call_args[0][0]
    assert len(actual_graph.nodes) == 2
    assert len(actual_graph.edges) == 1


@pytest.mark.parametrize("directed", [False, True])
def test_load(ref_id, persistence, directed):
    expected = nx.DiGraph() if directed else nx.Graph()
    a = ref_id("a", "test")
    b = ref_id("b", "test")
    expected.add_edge(a, b, weight=0.42, label=1)
    persistence.load.return_value = expected

    reference_graph = ReferenceGraph.load(persistence)

    assert len(reference_graph.nodes) == 2
    assert len(reference_graph.edges) == 1
    assert reference_graph.directed == directed
    assert reference_graph.has_edge(a, b)
    assert reference_graph.has_edge(b, a) == (not directed)
    assert reference_graph.weight(a, b) == 0.42
    assert reference_graph.weight(b, a) == (0.42 if not directed else 0.0)
    assert reference_graph.label(a, b) == 1
    assert reference_graph.label(b, a) == 0 if directed else 1


@pytest.mark.parametrize("is_directed", [False, True], indirect=["is_directed"])
def test_to_directed(is_directed, reference_graph, match_prediction):
    reference_graph.add(match_prediction)

    result = reference_graph.to_directed()

    assert isinstance(result, ReferenceGraph)
    assert result.directed
    left = match_prediction.left
    right = match_prediction.right
    assert result.has_edge(left, right)
    assert result.has_edge(right, left) == (not reference_graph.directed)
    assert result.weight(left, right) == 1.0
    assert result.weight(right, left) == (1.0 if not reference_graph.directed else 0.0)


@pytest.mark.parametrize("is_directed", [False, True], indirect=True)
def test_to_undirected(is_directed, reference_graph, match_prediction):
    reference_graph.add(match_prediction)

    result = reference_graph.to_undirected()

    assert isinstance(result, ReferenceGraph)
    assert not result.directed
    left = match_prediction.left
    right = match_prediction.right
    assert result.has_edge(left, right)
    assert result.has_edge(right, left)
    assert isclose(result.weight(left, right), 1)
    assert isclose(result.weight(right, left), 1)


@pytest.mark.parametrize(
    "is_directed,label,weights,prediction,fwd_weight,rev_weight",
    [
        (True, 0, [0.27, 0.26, 0.24, 0.23], 0, 0, 0),
        (True, 1, [0.27, 0.26, 0.24, 0.23], 1, 0.26, 0.26),
        (True, 2, [0.27, 0.26, 0.24, 0.23], 2, 0.24, 0.0),
        (False, 0, [0.27, 0.26, 0.24, 0.23], 0, 0, 0),
        (False, 1, [0.27, 0.26, 0.24, 0.23], 1, 0.26, 0.26),
        (False, 2, [0.27, 0.26, 0.24, 0.23], 1, 0.24, 0.24),
    ],
    indirect=["is_directed"],
)
def test_multiclass_weight_computation(
    is_directed,
    reference_graph,
    comparison,
    label,
    weights,
    prediction,
    fwd_weight,
    rev_weight,
):
    left, right = comparison

    reference_graph.add(MatchResult(left, right, label, weights))

    assert isclose(reference_graph.weight(left, right), fwd_weight)
    assert isclose(reference_graph.weight(right, left), rev_weight)
