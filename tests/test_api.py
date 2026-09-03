import pytest
from fastapi.testclient import TestClient

from app.data.repository import repository
from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("path", "expected_count", "id_path", "id_field", "expected_id"),
    [
        ("/companies", 200, "/companies/1", "company_id", 1),
        ("/supplies", 500, "/supplies/1", "supply_id", 1),
        ("/demands", 500, "/demands/1", "demand_id", 1),
        ("/preferences", 500, "/preferences/1", "preference_id", 1),
    ],
)
def test_list_and_detail_routes(
    client: TestClient,
    path: str,
    expected_count: int,
    id_path: str,
    id_field: str,
    expected_id: int,
) -> None:
    list_response = client.get(path)
    detail_response = client.get(id_path)

    assert list_response.status_code == 200
    assert len(list_response.json()) == expected_count
    assert detail_response.status_code == 200
    assert detail_response.json()[id_field] == expected_id


@pytest.mark.parametrize(
    "path",
    [
        "/companies/999999",
        "/supplies/999999",
        "/demands/999999",
        "/preferences/999999",
    ],
)
def test_detail_routes_return_404_for_unknown_ids(
    client: TestClient, path: str
) -> None:
    response = client.get(path)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_repository_can_resolve_updated_preference_by_user() -> None:
    preference = repository.get_preference_for_user(1)

    assert preference is not None
    assert preference.user_id == 1
    assert preference.preferred_sectors == ["E-commerce", "HealthTech"]
    assert preference.preferred_stages == ["Series B", "Pre-Seed"]
