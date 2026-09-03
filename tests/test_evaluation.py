import pytest

from app.recommendation.evaluation import compare_rankings, evaluate_ranking


def test_perfect_ranking_has_perfect_metrics() -> None:
    metrics = evaluate_ranking(
        labels=[3, 0, 2, 1, 3, 0],
        scores=[9, 1, 7, 4, 8, 2],
        groups=[3, 3],
    )

    assert metrics.ndcg_at_5 == pytest.approx(1.0)
    assert metrics.ndcg_at_10 == pytest.approx(1.0)
    assert metrics.recall_at_10 == pytest.approx(1.0)
    assert metrics.precision_at_10 == pytest.approx(0.5)
    assert metrics.hit_rate_at_10 == pytest.approx(1.0)


def test_comparison_returns_metrics_for_both_rankers() -> None:
    comparison = compare_rankings(
        labels=[3, 0, 2, 1],
        baseline_scores=[0.1, 0.9, 0.8, 0.7],
        ml_scores=[0.9, 0.2, 0.8, 0.1],
        groups=[4],
    )

    assert set(comparison.as_dict()) == {"baseline", "ml"}
    assert comparison.ml.ndcg_at_5 > comparison.baseline.ndcg_at_5


def test_evaluation_rejects_invalid_group_shape() -> None:
    with pytest.raises(ValueError, match="sum"):
        evaluate_ranking([1, 0], [0.5, 0.1], [1])
