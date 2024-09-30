from typing import Any

import pytest

from matchescu.similarity import ValueSimilarityMatch, MatchResult, Similarity


class SimilarityStub(Similarity):
    def __init__(self, sim_score: float = 0.5):
        self._sim_score = sim_score

    def _compute_similarity(self, _, __) -> float:
        return self._sim_score


def test_no_comparison_data():
    is_match = ValueSimilarityMatch(SimilarityStub())

    assert is_match(None, None) == MatchResult.NoComparisonData


@pytest.mark.parametrize("similarity, threshold, expected", [
    (0, 0.01, MatchResult.NonMatch),
    (1, 1, MatchResult.Match),
    (0.5, 0.49, MatchResult.Match),
])
def test_value_similarity_match(similarity, threshold, expected):
    is_match = ValueSimilarityMatch(SimilarityStub(similarity), threshold)

    assert is_match("any value", "stub method") == expected
