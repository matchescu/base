from dataclasses import dataclass


@dataclass(frozen=True)
class MatchResult:
    """The result output by a matcher.

    :param label: the prediction, according to the matcher's training/algorithm
    :param n_classes: the number of distinct classes that the matcher might return
    :param label_weights: the weight of each possible prediction of the matcher
        We assume the sum of the weights equals 1.
    """

    label: int
    label_weights: list[float]
