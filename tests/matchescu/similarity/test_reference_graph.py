from math import isclose
from unittest.mock import MagicMock

import networkx as nx
import pytest

from matchescu.similarity import MatchResult
from matchescu.similarity._matcher import Matcher
from matchescu.similarity._persistence import GraphPersistence
from matchescu.similarity._reference_graph import ReferenceGraph


@pytest.fixture
def persistence():
    return MagicMock(spec=GraphPersistence)


@pytest.fixture(scope="module")
def comparison_space(ref):
    return {(ref(1, "a"), ref(1, "b")), (ref(1, "b"), ref(1, "a"))}


def _match_result(match_prob: float) -> MatchResult:
    label = int(match_prob > 0.5)
    weights = [1 - match_prob, match_prob]
    return MatchResult(label, weights)


@pytest.fixture
def is_match(request):
    return getattr(request, "param", True)


@pytest.fixture
def mock_similarity(request):
    mock = MagicMock(name="mock_similarity", spec=Matcher)
    param = getattr(request, "param", 0.51)
    match param:
        case float():
            mock.return_value = _match_result(param)
        case MatchResult():
            mock.return_value = param
    return mock


@pytest.fixture
def is_directed(request):
    return bool(getattr(request, "param", True))


@pytest.fixture
def reference_graph(mock_similarity, is_directed):
    return ReferenceGraph(mock_similarity, directed=is_directed)


def test_sim_graph_calls_sim(comparison_space, reference_graph, mock_similarity):
    for a, b in comparison_space:
        reference_graph.add(a, b)

    assert mock_similarity.call_count == len(comparison_space)


@pytest.mark.parametrize(
    "is_directed,expected_matches",
    [(True, 2), (False, 1)],
    indirect=["is_directed"],
)
def test_add_match_edge(comparison_space, reference_graph, expected_matches):
    for a, b in comparison_space:
        reference_graph.add(a, b)

    matches = list(reference_graph.matches())

    assert len(matches) == expected_matches


@pytest.mark.parametrize(
    "is_directed,expected_matches",
    [(True, 2), (False, 1)],
    indirect=["is_directed"],
)
@pytest.mark.parametrize(
    "mock_similarity", [MatchResult(1, [0.45, 0.55])], indirect=True
)
def test_add_potential_match_edge(
    comparison_space, reference_graph, mock_similarity, expected_matches
):
    for a, b in comparison_space:
        reference_graph.add(a, b)

    potentials = list(reference_graph.potential_matches())

    assert len(potentials) == expected_matches


@pytest.mark.parametrize(
    "is_directed,expected_non_matches",
    [(True, 2), (False, 1)],
    indirect=["is_directed"],
)
def test_add_non_match(
    comparison_space, reference_graph, mock_similarity, expected_non_matches
):
    mock_similarity.return_value = MatchResult(0, [1, 0])
    for a, b in comparison_space:
        reference_graph.add(a, b)

    non_matches = list(reference_graph.non_matches())

    assert len(non_matches) == expected_non_matches


@pytest.mark.parametrize(
    "is_directed,expected",
    [(False, True), (True, False)],
    indirect=["is_directed"],
)
def test_has_edge_directed(reference_graph, ref, expected):
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    assert reference_graph.has_edge(b.id, a.id) == expected


@pytest.mark.parametrize(
    "mock_similarity",
    [MatchResult(0, [1, 0]), MatchResult(1, [0, 1])],
    indirect=["mock_similarity"],
)
def test_has_edge_is_match(reference_graph, ref, mock_similarity):
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    result_label = mock_similarity.return_value.label != 0
    assert reference_graph.has_edge(a.id, b.id) == result_label


def test_weight_directed(reference_graph, mock_similarity, ref):
    a = ref("a", "test")
    b = ref("b", "test")
    mock_similarity.side_effect = lambda x, y: (
        _match_result(0.51) if x == a else _match_result(0.6)
    )

    reference_graph.add(a, b)
    reference_graph.add(b, a)

    assert reference_graph.weight(a.id, b.id) == 0.51
    assert reference_graph.weight(b.id, a.id) == 0.6


@pytest.mark.parametrize("is_directed", [False], indirect=True)
def test_weight_undirected(reference_graph, mock_similarity, ref):
    a = ref("a", "test")
    b = ref("b", "test")
    mock_similarity.side_effect = lambda x, y: (
        _match_result(0.4) if x == a else _match_result(0.6)
    )

    reference_graph.add(a, b)
    reference_graph.add(b, a)

    assert reference_graph.weight(a.id, b.id) == 0.6
    assert reference_graph.weight(b.id, a.id) == 0.6


def test_save(reference_graph, ref, persistence):
    reference_graph.add(ref("a", "test"), ref("b", "test"))

    reference_graph.save(persistence)

    assert persistence.save.call_count == 1
    actual_graph = persistence.save.call_args[0][0]
    assert len(actual_graph.nodes) == 2
    assert len(actual_graph.edges) == 1


@pytest.mark.parametrize(
    "reference_graph,directed",
    [(False, True), (True, False)],
    indirect=["reference_graph"],
)
def test_load(reference_graph, ref, persistence, directed):
    expected = nx.DiGraph() if directed else nx.Graph()
    a = ref("a", "test")
    b = ref("b", "test")
    expected.add_edge(a.id, b.id, weight=0.42)
    persistence.load.return_value = expected

    reference_graph.load(persistence)

    assert len(reference_graph.nodes) == 2
    assert len(reference_graph.edges) == 1
    assert reference_graph.directed == directed
    assert reference_graph.has_edge(a.id, b.id)
    assert reference_graph.has_edge(b.id, a.id) == (not directed)
    assert reference_graph.weight(a.id, b.id) == 0.42
    assert reference_graph.weight(b.id, a.id) == (0.42 if not directed else 0.0)


@pytest.mark.parametrize("is_directed", [False, True], indirect=["is_directed"])
def test_to_directed(reference_graph, ref, mock_similarity):
    mock_similarity.side_effect = lambda x, y: (
        _match_result(0.51) if x == a else _match_result(0.6)
    )
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    result = reference_graph.to_directed()

    assert isinstance(result, ReferenceGraph)
    assert result.directed
    assert result.has_edge(a.id, b.id)
    assert result.has_edge(b.id, a.id) == (not reference_graph.directed)
    assert result.weight(a.id, b.id) == 0.51
    assert result.weight(b.id, a.id) == (0.6 if not reference_graph.directed else 0.0)


@pytest.mark.parametrize(
    "is_directed,mock_similarity", [(False, 0.52), (True, 0.52)], indirect=True
)
def test_to_undirected(reference_graph, ref, mock_similarity, is_directed):
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    result = reference_graph.to_undirected()

    assert isinstance(result, ReferenceGraph)
    assert not result.directed
    assert result.has_edge(a.id, b.id)
    assert result.has_edge(b.id, a.id)
    assert isclose(result.weight(a.id, b.id), 0.52)
    assert isclose(result.weight(b.id, a.id), 0.52)


@pytest.mark.parametrize(
    "is_directed,mock_similarity,weight_ab, weight_ba",
    [
        (True, MatchResult(0, [0.27, 0.26, 0.24, 0.23]), 0, 0),
        (True, MatchResult(1, [0.27, 0.26, 0.24, 0.23]), 0.26, 0.26),
        (True, MatchResult(2, [0.27, 0.26, 0.24, 0.23]), 0.24, 0.0),
        (True, MatchResult(3, [0.27, 0.26, 0.24, 0.23]), 0.0, 0.23),
    ],
    indirect=["mock_similarity", "is_directed"],
)
def test_default_weight_computation(
    reference_graph, ref, mock_similarity, weight_ab, weight_ba
):
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    assert isclose(reference_graph.weight(a.id, b.id), weight_ab)
    assert isclose(reference_graph.weight(b.id, a.id), weight_ba)
