import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.matching.engine import MatchingEngine


def test_supply_matching_returns_ranked_same_currency_demands() -> None:
    matches = MatchingEngine().match_supply(1, limit=10)

    assert len(matches) == 10
    assert all(match.supply.supply_id == 1 for match in matches)
    assert all(match.supply.currency == match.demand.currency for match in matches)
    assert all(matches[index].score.total_score >= matches[index + 1].score.total_score for index in range(len(matches) - 1))
    assert all(0 <= match.score.total_score <= 100 for match in matches)


def test_demand_matching_returns_ranked_same_currency_supplies() -> None:
    matches = MatchingEngine().match_demand(1, limit=10)

    assert len(matches) == 10
    assert all(match.demand.demand_id == 1 for match in matches)
    assert all(match.supply.currency == match.demand.currency for match in matches)


def test_matching_never_returns_cross_currency_candidates() -> None:
    supply_matches = MatchingEngine().match_supply(1, limit=100)
    demand_matches = MatchingEngine().match_demand(1, limit=100)

    assert all(match.supply.currency == match.demand.currency for match in supply_matches)
    assert all(match.supply.currency == match.demand.currency for match in demand_matches)


def test_missing_preference_is_an_explicit_error() -> None:
    with pytest.raises(LookupError, match="preferences"):
        MatchingEngine()._preference_or_error(999999)


def test_match_routes_return_pair_and_score_breakdown() -> None:
    with TestClient(app) as client:
        response = client.get("/matches/supply/1?limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert {"supply", "demand", "score", "score_breakdown", "reasons"}.issubset(payload[0])
    assert set(payload[0]["score_breakdown"]) == {
        "company_sector_alignment",
        "valuation_fit",
        "deal_size_fit",
        "stage_fit",
        "price_reasonableness",
    }


def test_match_route_returns_404_for_unknown_supply() -> None:
    with TestClient(app) as client:
        response = client.get("/matches/supply/999999")

    assert response.status_code == 404
    assert "Supply" in response.json()["detail"]
