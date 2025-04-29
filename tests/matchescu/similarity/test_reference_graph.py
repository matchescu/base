from unittest.mock import MagicMock

import networkx as nx
import pytest

from matchescu.similarity._matcher import Matcher
from matchescu.similarity._persistence import GraphPersistence
from matchescu.similarity._reference_graph import ReferenceGraph


@pytest.fixture
def persistence():
    return MagicMock(spec=GraphPersistence)


@pytest.fixture(scope="module")
def comparison_space(ref):
    return {(ref(1, "a"), ref(1, "b")), (ref(1, "b"), ref(1, "a"))}


@pytest.fixture
def mock_similarity(request):
    mock = MagicMock(name="mock_similarity", spec=Matcher)
    mock.return_value = request.param if hasattr(request, "param") else 0.5
    return mock


@pytest.fixture
def reference_graph(mock_similarity, request):
    return ReferenceGraph(
        mock_similarity,
        directed=((not hasattr(request, "param")) or bool(request.param)),
    )


def test_sim_graph_calls_sim(comparison_space, reference_graph, mock_similarity):
    for a, b in comparison_space:
        reference_graph.add(a, b)

    assert mock_similarity.call_count == len(comparison_space)


@pytest.mark.parametrize(
    "reference_graph,expected_matches",
    [(True, 2), (False, 1)],
    indirect=["reference_graph"],
)
def test_add_match_edge(
    comparison_space, reference_graph, mock_similarity, expected_matches
):
    mock_similarity.return_value = 0.75
    for a, b in comparison_space:
        reference_graph.add(a, b)

    matches = list(reference_graph.matches())

    assert len(matches) == expected_matches


@pytest.mark.parametrize(
    "reference_graph,expected_matches",
    [(True, 2), (False, 1)],
    indirect=["reference_graph"],
)
def test_add_potential_match_edge(
    comparison_space, reference_graph, mock_similarity, expected_matches
):
    mock_similarity.return_value = 0.5
    for a, b in comparison_space:
        reference_graph.add(a, b)

    potentials = list(reference_graph.potential_matches())

    assert len(potentials) == expected_matches


@pytest.mark.parametrize(
    "reference_graph,expected_non_matches",
    [(True, 2), (False, 1)],
    indirect=["reference_graph"],
)
def test_add_non_match(
    comparison_space, reference_graph, mock_similarity, expected_non_matches
):
    mock_similarity.return_value = 0.24
    for a, b in comparison_space:
        reference_graph.add(a, b)

    non_matches = list(reference_graph.non_matches())

    assert len(non_matches) == expected_non_matches


@pytest.mark.parametrize(
    "reference_graph,expected",
    [(False, True), (True, False)],
    indirect=["reference_graph"],
)
def test_has_edge(reference_graph, ref, expected):
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    assert reference_graph.has_edge(b.id, a.id) == expected


def test_weight_directed(reference_graph, mock_similarity, ref):
    a = ref("a", "test")
    b = ref("b", "test")
    mock_similarity.side_effect = lambda x, y: 0.4 if x == a else 0.6

    reference_graph.add(a, b)
    reference_graph.add(b, a)

    assert reference_graph.weight(a.id, b.id) == 0.4
    assert reference_graph.weight(b.id, a.id) == 0.6


@pytest.mark.parametrize("reference_graph", [False], indirect=True)
def test_weight_undirected(reference_graph, mock_similarity, ref):
    a = ref("a", "test")
    b = ref("b", "test")
    mock_similarity.side_effect = lambda x, y: 0.4 if x == a else 0.6

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


@pytest.mark.parametrize("reference_graph", [False, True], indirect=["reference_graph"])
def test_to_directed(reference_graph, ref, mock_similarity):
    mock_similarity.side_effect = lambda x, y: 0.4 if x == a else 0.6
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    result = reference_graph.to_directed()

    assert isinstance(result, ReferenceGraph)
    assert result.directed
    assert result.has_edge(a.id, b.id)
    assert result.has_edge(b.id, a.id) == (not reference_graph.directed)
    assert result.weight(a.id, b.id) == 0.4
    assert result.weight(b.id, a.id) == (0.6 if not reference_graph.directed else 0.0)


@pytest.mark.parametrize("reference_graph", [False, True], indirect=["reference_graph"])
def test_to_undirected(reference_graph, ref, mock_similarity):
    mock_similarity.return_value = 0.42
    a = ref("a", "test")
    b = ref("b", "test")
    reference_graph.add(a, b)

    result = reference_graph.to_undirected()

    assert isinstance(result, ReferenceGraph)
    assert not result.directed
    assert result.has_edge(a.id, b.id)
    assert result.has_edge(b.id, a.id)
    assert result.weight(b.id, a.id) == result.weight(a.id, b.id) == 0.42
