import pytest

from app.recommendation.ranking import BaselineRanker, BaselineWeights


def test_baseline_returns_ranked_candidates_with_explanations() -> None:
    results = BaselineRanker().rank(user_id=1, limit=10)

    assert len(results) == 10
    assert all(0 <= result.breakdown.total_score <= 100 for result in results)
    assert all(result.breakdown.dimension_scores for result in results)
    assert all(result.breakdown.reasons for result in results)
    assert [result.breakdown.total_score for result in results] == sorted(
        (result.breakdown.total_score for result in results), reverse=True
    )


def test_baseline_weights_are_configurable() -> None:
    ranker = BaselineRanker(
        weights=BaselineWeights(
            sector_match=100,
            valuation_match=0,
            stage_match=0,
            geography_match=0,
            historical_interest=0,
            popularity=0,
        )
    )
    results = ranker.rank(user_id=1, limit=10)

    assert all(
        result.breakdown.total_score in (0.0, 100.0)
        for result in results
    )
    assert all(
        result.breakdown.dimension_scores["valuation_match"] == 0.0
        for result in results
    )


def test_negative_or_empty_weights_are_rejected() -> None:
    with pytest.raises(ValueError, match="negative"):
        BaselineWeights(sector_match=-1)

    with pytest.raises(ValueError, match="positive"):
        BaselineWeights(
            sector_match=0,
            valuation_match=0,
            stage_match=0,
            geography_match=0,
            historical_interest=0,
            popularity=0,
        )


def test_limit_zero_returns_no_recommendations() -> None:
    assert BaselineRanker().rank(user_id=1, limit=0) == []
