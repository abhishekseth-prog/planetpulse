import pytest
from datetime import date
from tests.conftest import client, TestingSessionLocal
from app.models.activity import Activity


def test_get_activities_empty(client):
    """GET /api/activities returns empty list when no activities exist."""
    response = client.get("/api/activities")
    assert response.status_code == 200
    assert response.json() == []


def test_get_activities_populated(client):
    """GET /api/activities returns stored activities."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 20), co2e=2.1))
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=date(2026, 9, 21), co2e=1.8))
    db.commit()
    db.close()

    response = client.get("/api/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verify order is descending by date
    assert data[0]["date"] == "2026-09-21"
    assert data[1]["date"] == "2026-09-20"


def test_get_activities_category_filter(client):
    """GET /api/activities?category=travel returns only travel activities."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 20), co2e=2.1))
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=date(2026, 9, 21), co2e=1.8))
    db.commit()
    db.close()

    response = client.get("/api/activities?category=travel")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "travel"


def test_get_activities_date_filter(client):
    """GET /api/activities with start_date and end_date filtering."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 10), co2e=2.1))
    db.add(Activity(category="travel", activity="bus", amount=15.0, unit="km", date=date(2026, 9, 20), co2e=1.5))
    db.add(Activity(category="travel", activity="train", amount=50.0, unit="km", date=date(2026, 9, 28), co2e=2.0))
    db.commit()
    db.close()

    response = client.get("/api/activities?start_date=2026-09-15&end_date=2026-09-25")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["date"] == "2026-09-20"


def test_get_activities_invalid_date_range(client):
    """GET /api/activities with start_date > end_date returns 422."""
    response = client.get("/api/activities?start_date=2026-09-28&end_date=2026-09-10")
    assert response.status_code == 422
