import pytest
from datetime import date
from app.models.activity import Activity
from tests.conftest import client, TestingSessionLocal


# -----------------------------------------------------------------------------
# 1. Empty Database
# -----------------------------------------------------------------------------
def test_trend_empty_database(client):
    """GET /api/trend with empty database returns {'trend': []}."""
    response = client.get("/api/trend")
    assert response.status_code == 200
    data = response.json()
    assert "trend" in data
    assert data["trend"] == []


# -----------------------------------------------------------------------------
# 2. Single Activity
# -----------------------------------------------------------------------------
def test_trend_single_activity(client):
    """Verify single activity returns one point with matching co2e and count."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 27), co2e=4.2))
    db.commit()
    db.close()

    response = client.get("/api/trend")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trend"]) == 1
    point = data["trend"][0]
    assert point["date"] == "2026-09-27"
    assert point["co2e"] == 4.2
    assert point["activities"] == 1


# -----------------------------------------------------------------------------
# 3, 7. Multiple Activities on Different Dates & Chronological Ordering
# -----------------------------------------------------------------------------
def test_trend_multiple_dates_chronological_ordering(client):
    """Verify multiple dates are returned strictly in ascending chronological order."""
    db = TestingSessionLocal()
    # Insert in non-chronological order
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=date(2026, 9, 27), co2e=1.8))
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 10), co2e=4.2))
    db.add(Activity(category="electricity", activity="ac", amount=5.0, unit="hours", date=date(2026, 9, 20), co2e=3.375))
    db.commit()
    db.close()

    response = client.get("/api/trend")
    assert response.status_code == 200
    data = response.json()
    trend = data["trend"]
    assert len(trend) == 3

    assert trend[0]["date"] == "2026-09-10"
    assert trend[0]["co2e"] == 4.2
    assert trend[0]["activities"] == 1

    assert trend[1]["date"] == "2026-09-20"
    assert pytest.approx(trend[1]["co2e"], rel=1e-4) == 3.375
    assert trend[1]["activities"] == 1

    assert trend[2]["date"] == "2026-09-27"
    assert trend[2]["co2e"] == 1.8
    assert trend[2]["activities"] == 1


# -----------------------------------------------------------------------------
# 4, 5, 6. Multiple Activities on Same Date & Same-Day Aggregation
# -----------------------------------------------------------------------------
def test_trend_same_day_aggregation(client):
    """Verify that multiple activities on the same date are grouped into a single entry."""
    db = TestingSessionLocal()
    # On 2026-09-27: car (4.2) + chicken (1.8) + ac (3.375) = 9.375, 3 activities
    target_date = date(2026, 9, 27)
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=target_date, co2e=4.2))
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=target_date, co2e=1.8))
    db.add(Activity(category="electricity", activity="ac", amount=5.0, unit="hours", date=target_date, co2e=3.375))
    db.commit()
    db.close()

    response = client.get("/api/trend")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trend"]) == 1
    point = data["trend"][0]
    assert point["date"] == "2026-09-27"
    assert pytest.approx(point["co2e"], rel=1e-4) == 9.375
    assert point["activities"] == 3


# -----------------------------------------------------------------------------
# 8. Start Date Filtering
# -----------------------------------------------------------------------------
def test_trend_start_date_filtering(client):
    """GET /api/trend?start_date=YYYY-MM-DD includes only activities >= start_date."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 5), co2e=2.1))
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 20), co2e=4.2))
    db.commit()
    db.close()

    response = client.get("/api/trend?start_date=2026-09-10")
    assert response.status_code == 200
    trend = response.json()["trend"]
    assert len(trend) == 1
    assert trend[0]["date"] == "2026-09-20"
    assert trend[0]["co2e"] == 4.2


# -----------------------------------------------------------------------------
# 9. End Date Filtering
# -----------------------------------------------------------------------------
def test_trend_end_date_filtering(client):
    """GET /api/trend?end_date=YYYY-MM-DD includes only activities <= end_date."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 5), co2e=2.1))
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 25), co2e=4.2))
    db.commit()
    db.close()

    response = client.get("/api/trend?end_date=2026-09-10")
    assert response.status_code == 200
    trend = response.json()["trend"]
    assert len(trend) == 1
    assert trend[0]["date"] == "2026-09-05"
    assert trend[0]["co2e"] == 2.1


# -----------------------------------------------------------------------------
# 10 & 14. Start + End Date Filtering & Excluding Out-of-Range Activities
# -----------------------------------------------------------------------------
def test_trend_start_and_end_date_filtering(client):
    """GET /api/trend with both start_date and end_date filters inclusively."""
    db = TestingSessionLocal()
    # Before range (August)
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 8, 31), co2e=2.1))
    # Inside range
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 10), co2e=4.2))
    db.add(Activity(category="electricity", activity="ac", amount=5.0, unit="hours", date=date(2026, 9, 20), co2e=3.375))
    # After range (October)
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=date(2026, 10, 1), co2e=1.8))
    db.commit()
    db.close()

    response = client.get("/api/trend?start_date=2026-09-01&end_date=2026-09-27")
    assert response.status_code == 200
    trend = response.json()["trend"]
    assert len(trend) == 2
    assert trend[0]["date"] == "2026-09-10"
    assert trend[1]["date"] == "2026-09-20"


# -----------------------------------------------------------------------------
# 11. Invalid Start Date
# -----------------------------------------------------------------------------
def test_trend_invalid_start_date_returns_422(client):
    """Malformed start_date returns HTTP 422."""
    response = client.get("/api/trend?start_date=invalid-date")
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 12. Invalid End Date
# -----------------------------------------------------------------------------
def test_trend_invalid_end_date_returns_422(client):
    """Malformed end_date returns HTTP 422."""
    response = client.get("/api/trend?end_date=2026-99-99")
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 13. start_date > end_date Error
# -----------------------------------------------------------------------------
def test_trend_start_date_greater_than_end_date_returns_422(client):
    """When start_date > end_date, return HTTP 422 error without swapping."""
    response = client.get("/api/trend?start_date=2026-09-27&end_date=2026-09-01")
    assert response.status_code == 422
    assert "cannot be greater than end_date" in response.json()["detail"]


# -----------------------------------------------------------------------------
# 15 & 16. Stored co2e is Used Directly & Carbon Engine Not Called
# -----------------------------------------------------------------------------
def test_trend_uses_stored_co2e_directly(client):
    """Ensure trend aggregates stored co2e and never calls calculate_co2e."""
    db = TestingSessionLocal()
    # Insert with a deliberate arbitrary stored co2e
    db.add(Activity(category="travel", activity="car", amount=1.0, unit="km", date=date(2026, 9, 27), co2e=88.8))
    db.commit()
    db.close()

    response = client.get("/api/trend")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trend"]) == 1
    assert data["trend"][0]["co2e"] == 88.8
