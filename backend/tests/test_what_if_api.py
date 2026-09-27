import pytest
from tests.conftest import client


def test_what_if_nested_format(client):
    """POST /api/what-if with nested format computes emission reduction."""
    payload = {
        "current": {
            "activity": "car",
            "amount": 20,
            "unit": "km",
        },
        "alternative": {
            "activity": "metro",
            "amount": 20,
            "unit": "km",
        },
    }
    response = client.post("/api/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2"] == pytest.approx(4.2, rel=1e-3)
    assert data["new_co2"] == pytest.approx(0.6, rel=1e-3)
    assert data["daily_reduction"] == pytest.approx(3.6, rel=1e-3)
    assert data["monthly_reduction"] == pytest.approx(108.0, rel=1e-3)
    assert data["is_reduction"] is True
    assert data["reduction_percent"] > 0


def test_what_if_flat_format(client):
    """POST /api/what-if with frontend flat contract format."""
    payload = {
        "category": "travel",
        "current_activity": "car",
        "alternative_activity": "bus",
        "distance": 20,
        "unit": "km",
    }
    response = client.post("/api/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2"] == pytest.approx(4.2, rel=1e-3)
    assert data["new_co2"] == pytest.approx(2.0, rel=1e-3)
    assert data["daily_reduction"] == pytest.approx(2.2, rel=1e-3)
    assert data["is_reduction"] is True


def test_what_if_non_reduction_scenario(client):
    """POST /api/what-if where alternative has higher emissions."""
    payload = {
        "current": {
            "activity": "bus",
            "amount": 20,
            "unit": "km",
        },
        "alternative": {
            "activity": "car",
            "amount": 20,
            "unit": "km",
        },
    }
    response = client.post("/api/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["daily_reduction"] < 0
    assert data["is_reduction"] is False


def test_what_if_invalid_activity(client):
    """POST /api/what-if with unsupported activity returns 400."""
    payload = {
        "current": {
            "activity": "rocket_ship",
            "amount": 20,
            "unit": "km",
        },
        "alternative": {
            "activity": "metro",
            "amount": 20,
            "unit": "km",
        },
    }
    response = client.post("/api/what-if", json=payload)
    assert response.status_code == 400


def test_what_if_missing_scenarios(client):
    """POST /api/what-if with missing scenarios returns 422."""
    payload = {"current": {"activity": "car", "amount": 20, "unit": "km"}}
    response = client.post("/api/what-if", json=payload)
    assert response.status_code == 422
