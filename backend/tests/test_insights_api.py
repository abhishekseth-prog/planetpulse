import pytest
from datetime import date
from tests.conftest import client, TestingSessionLocal
from app.models.activity import Activity


def test_insights_empty_activities(client):
    """GET /api/insights when database has no activities."""
    response = client.get("/api/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["largest_contributor"] == "None"
    assert data["contribution_percent"] == 0.0
    assert "Start logging activities" in data["opportunity"]
    assert data["potential_impact_kg"] == 0.0
    assert data["method"] == "rule_based"


def test_insights_travel_highest(client):
    """GET /api/insights when travel has highest emissions."""
    today = date.today()
    db = TestingSessionLocal()
    # Travel: 20 km * 0.21 = 4.2 kg
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=today, co2e=4.2))
    # Food: 1 meal * 0.8 = 0.8 kg
    db.add(Activity(category="food", activity="vegetarian_meal", amount=1.0, unit="meal", date=today, co2e=0.8))
    db.commit()
    db.close()

    response = client.get("/api/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["largest_contributor"] == "Travel"
    assert data["contribution_percent"] > 80.0
    assert "public transit" in data["opportunity"]
    assert len(data["actions"]) > 0
    assert data["potential_impact_kg"] == pytest.approx(0.4, rel=1e-1)


def test_insights_food_highest(client):
    """GET /api/insights when food has highest emissions."""
    today = date.today()
    db = TestingSessionLocal()
    # Food: 2 meals * 6.5 = 13.0 kg
    db.add(Activity(category="food", activity="beef_meal", amount=2.0, unit="meal", date=today, co2e=13.0))
    # Travel: 5 km * 0.21 = 1.05 kg
    db.add(Activity(category="travel", activity="car", amount=5.0, unit="km", date=today, co2e=1.05))
    db.commit()
    db.close()

    response = client.get("/api/insights")
    assert response.status_code == 200
    data = response.json()
    assert data["largest_contributor"] == "Food"
    assert "lower-impact meals" in data["opportunity"]
    assert len(data["actions"]) > 0
