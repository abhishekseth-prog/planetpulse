import pytest
from datetime import date
from tests.conftest import client, TestingSessionLocal
from app.models.activity import Activity


def test_get_monthly_goal_default(client):
    """GET /api/goals/monthly returns default goal progress."""
    response = client.get("/api/goals/monthly")
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == 100.0
    assert data["current"] == 0.0
    assert data["progress"] == 0.0
    assert data["remaining"] == 100.0


def test_put_monthly_goal_update(client):
    """PUT /api/goals/monthly updates the monthly target."""
    payload = {"target": 150.0}
    response = client.put("/api/goals/monthly", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == 150.0
    assert data["remaining"] == 150.0

    # Verify subsequent GET reflects new target
    get_res = client.get("/api/goals/monthly")
    assert get_res.status_code == 200
    assert get_res.json()["target"] == 150.0


def test_put_monthly_goal_invalid_target(client):
    """PUT /api/goals/monthly with non-positive target returns 422."""
    payload = {"target": -10.0}
    response = client.put("/api/goals/monthly", json=payload)
    assert response.status_code == 422


def test_monthly_goal_with_activities(client):
    """GET /api/goals/monthly accurately computes current and remaining."""
    today = date.today()
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=today, co2e=4.2))
    db.add(Activity(category="electricity", activity="ac", amount=4.0, unit="hours", date=today, co2e=2.7))
    db.commit()
    db.close()

    response = client.get("/api/goals/monthly")
    assert response.status_code == 200
    data = response.json()
    assert data["current"] == pytest.approx(6.9, rel=1e-3)
    assert data["progress"] == pytest.approx(6.9, rel=1e-3)
    assert data["remaining"] == pytest.approx(93.1, rel=1e-3)
