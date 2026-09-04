import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.recommendation.recommender import RecommendationEngine


def test_engine_returns_explained_baseline_recommendations() -> None:
    recommendations = RecommendationEngine().get_recommendations(1, limit=10)

    assert len(recommendations) == 10
    assert all(item.company_id > 0 for item in recommendations)
    assert all(item.reasons for item in recommendations)
    assert len({item.company_id for item in recommendations}) == 10


def test_engine_handles_unknown_user_with_popular_fallback() -> None:
    recommendations = RecommendationEngine().get_recommendations(999999, limit=5)

    assert len(recommendations) == 5
    assert all("popular" in item.sources for item in recommendations)


def test_engine_rejects_unknown_model() -> None:
    with pytest.raises(ValueError, match="model"):
        RecommendationEngine().get_recommendations(1, model="unknown")


def test_recommendation_api_returns_json() -> None:
    with TestClient(app) as client:
        response = client.get("/recommendations/1?limit=3")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert {"company_id", "score", "reasons", "sources"}.issubset(response.json()[0])