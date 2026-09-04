from dataclasses import dataclass
from math import log2
from typing import Sequence


@dataclass(frozen=True)
class RankingMetrics:
    ndcg_at_5: float
    ndcg_at_10: float
    recall_at_10: float
    precision_at_10: float
    hit_rate_at_10: float

    def as_dict(self) -> dict[str, float]:
        return {
            "ndcg_at_5": self.ndcg_at_5,
            "ndcg_at_10": self.ndcg_at_10,
            "recall_at_10": self.recall_at_10,
            "precision_at_10": self.precision_at_10,
            "hit_rate_at_10": self.hit_rate_at_10,
        }


@dataclass(frozen=True)
class RankingComparison:
    baseline: RankingMetrics
    ml: RankingMetrics

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {"baseline": self.baseline.as_dict(), "ml": self.ml.as_dict()}


def evaluate_ranking(
    labels: Sequence[int],
    scores: Sequence[float],
    groups: Sequence[int],
    positive_label: int = 2,
) -> RankingMetrics:
    """Evaluate grouped ranking scores using one aggregate per user."""
    _validate_inputs(labels, scores, groups, positive_label)
    ndcg5: list[float] = []
    ndcg10: list[float] = []
    recalls: list[float] = []
    precisions: list[float] = []
    hits: list[float] = []
    offset = 0
    for group_size in groups:
        group_labels = list(labels[offset : offset + group_size])
        group_scores = list(scores[offset : offset + group_size])
        offset += group_size
        order = sorted(range(group_size), key=lambda index: (-group_scores[index], index))
        ranked_labels = [group_labels[index] for index in order]
        ndcg5.append(_ndcg(group_labels, ranked_labels, 5))
        ndcg10.append(_ndcg(group_labels, ranked_labels, 10))

        relevant = sum(label >= positive_label for label in group_labels)
        recommended = ranked_labels[:10]
        relevant_recommended = sum(label >= positive_label for label in recommended)
        recalls.append(relevant_recommended / relevant if relevant else 0.0)
        precisions.append(relevant_recommended / len(recommended) if recommended else 0.0)
        hits.append(float(relevant_recommended > 0))

    return RankingMetrics(
        ndcg_at_5=_average(ndcg5),
        ndcg_at_10=_average(ndcg10),
        recall_at_10=_average(recalls),
        precision_at_10=_average(precisions),
        hit_rate_at_10=_average(hits),
    )


def compare_rankings(
    labels: Sequence[int],
    baseline_scores: Sequence[float],
    ml_scores: Sequence[float],
    groups: Sequence[int],
    positive_label: int = 2,
) -> RankingComparison:
    return RankingComparison(
        baseline=evaluate_ranking(labels, baseline_scores, groups, positive_label),
        ml=evaluate_ranking(labels, ml_scores, groups, positive_label),
    )


def _ndcg(labels: Sequence[int], ranked_labels: Sequence[int], cutoff: int) -> float:
    actual = sum(
        (2**label - 1) / log2(index + 2)
        for index, label in enumerate(ranked_labels[:cutoff])
    )
    ideal_labels = sorted(labels, reverse=True)
    ideal = sum(
        (2**label - 1) / log2(index + 2)
        for index, label in enumerate(ideal_labels[:cutoff])
    )
    return actual / ideal if ideal else 0.0


def _average(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _validate_inputs(
    labels: Sequence[int],
    scores: Sequence[float],
    groups: Sequence[int],
    positive_label: int,
) -> None:
    if len(labels) != len(scores):
        raise ValueError("Labels and scores must have the same length")
    if not groups or sum(groups) != len(labels):
        raise ValueError("Groups must be non-empty and sum to row count")
    if positive_label < 0:
        raise ValueError("positive_label cannot be negative")
