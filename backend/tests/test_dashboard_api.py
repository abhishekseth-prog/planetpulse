import pytest
from datetime import date
from app.models.activity import Activity
from tests.conftest import client, TestingSessionLocal


# -----------------------------------------------------------------------------
# 1. Dashboard with No Activities (Empty DB)
# -----------------------------------------------------------------------------
def test_dashboard_empty_database(client):
    """GET /api/dashboard with empty database returns 0.0 totals and empty categories."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_co2"] == 0.0
    assert data["total_activities"] == 0
    assert data["categories"]["travel"] == {"co2e": 0.0, "activities": 0}
    assert data["categories"]["electricity"] == {"co2e": 0.0, "activities": 0}
    assert data["categories"]["food"] == {"co2e": 0.0, "activities": 0}


# -----------------------------------------------------------------------------
# 2. Dashboard with One Activity
# -----------------------------------------------------------------------------
def test_dashboard_single_activity(client):
    """Verify single activity aggregation."""
    db = TestingSessionLocal()
    act = Activity(
        category="travel",
        activity="car",
        amount=20.0,
        unit="km",
        date=date(2026, 9, 27),
        co2e=4.2,
    )
    db.add(act)
    db.commit()
    db.close()

    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_co2"] == 4.2
    assert data["total_activities"] == 1
    assert data["categories"]["travel"] == {"co2e": 4.2, "activities": 1}
    assert data["categories"]["electricity"] == {"co2e": 0.0, "activities": 0}
    assert data["categories"]["food"] == {"co2e": 0.0, "activities": 0}


# -----------------------------------------------------------------------------
# 3, 4, 5, 6, 7, 8. Multiple Activities, Correct Totals & Breakdown
# -----------------------------------------------------------------------------
def test_dashboard_multiple_activities_totals_and_breakdowns(client):
    """Verify multiple activity aggregation across all 3 categories."""
    db = TestingSessionLocal()
    # 20 km car = 4.2
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 27), co2e=4.2))
    # 5 hours ac = 3.375
    db.add(Activity(category="electricity", activity="ac", amount=5.0, unit="hours", date=date(2026, 9, 27), co2e=3.375))
    # 1 chicken meal = 1.8 (or 2.0)
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=date(2026, 9, 27), co2e=2.0))
    db.commit()
    db.close()

    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    # total_co2 = 4.2 + 3.375 + 2.0 = 9.575
    assert pytest.approx(data["total_co2"], rel=1e-4) == 9.575
    assert data["total_activities"] == 3
    assert data["categories"]["travel"] == {"co2e": 4.2, "activities": 1}
    assert pytest.approx(data["categories"]["electricity"]["co2e"], rel=1e-4) == 3.375
    assert data["categories"]["electricity"]["activities"] == 1
    assert data["categories"]["food"] == {"co2e": 2.0, "activities": 1}


# -----------------------------------------------------------------------------
# 9. Multiple Activities in Same Category
# -----------------------------------------------------------------------------
def test_multiple_activities_same_category(client):
    """Verify category sums when multiple activities exist in one category."""
    db = TestingSessionLocal()
    # Travel: car (4.2) + bus (1.0)
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 27), co2e=4.2))
    db.add(Activity(category="travel", activity="bus", amount=10.0, unit="km", date=date(2026, 9, 27), co2e=1.0))
    db.commit()
    db.close()

    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert pytest.approx(data["total_co2"], rel=1e-4) == 5.2
    assert data["total_activities"] == 2
    assert pytest.approx(data["categories"]["travel"]["co2e"], rel=1e-4) == 5.2
    assert data["categories"]["travel"]["activities"] == 2


# -----------------------------------------------------------------------------
# 10. Start Date Filtering
# -----------------------------------------------------------------------------
def test_start_date_filtering(client):
    """GET /api/dashboard?start_date=YYYY-MM-DD includes only activities on or after start_date."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 10), co2e=2.1))
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 20), co2e=4.2))
    db.commit()
    db.close()

    response = client.get("/api/dashboard?start_date=2026-09-15")
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 1
    assert pytest.approx(data["total_co2"], rel=1e-4) == 4.2


# -----------------------------------------------------------------------------
# 11. End Date Filtering
# -----------------------------------------------------------------------------
def test_end_date_filtering(client):
    """GET /api/dashboard?end_date=YYYY-MM-DD includes only activities on or before end_date."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 10), co2e=2.1))
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 25), co2e=4.2))
    db.commit()
    db.close()

    response = client.get("/api/dashboard?end_date=2026-09-15")
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 1
    assert pytest.approx(data["total_co2"], rel=1e-4) == 2.1


# -----------------------------------------------------------------------------
# 12 & 16. Start + End Date Filtering & Excluding Out-of-Range Activities
# -----------------------------------------------------------------------------
def test_start_and_end_date_filtering(client):
    """GET /api/dashboard with both start_date and end_date filters inclusively."""
    db = TestingSessionLocal()
    # Before window
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=date(2026, 9, 1), co2e=2.1))
    # Inside window
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=date(2026, 9, 15), co2e=4.2))
    # After window
    db.add(Activity(category="travel", activity="car", amount=30.0, unit="km", date=date(2026, 9, 30), co2e=6.3))
    db.commit()
    db.close()

    response = client.get("/api/dashboard?start_date=2026-09-10&end_date=2026-09-20")
    assert response.status_code == 200
    data = response.json()
    assert data["total_activities"] == 1
    assert pytest.approx(data["total_co2"], rel=1e-4) == 4.2


# -----------------------------------------------------------------------------
# 13. Invalid Start Date
# -----------------------------------------------------------------------------
def test_invalid_start_date_returns_422(client):
    """Malformed start_date returns HTTP 422."""
    response = client.get("/api/dashboard?start_date=invalid-date")
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 14. Invalid End Date
# -----------------------------------------------------------------------------
def test_invalid_end_date_returns_422(client):
    """Malformed end_date returns HTTP 422."""
    response = client.get("/api/dashboard?end_date=2026-15-40")
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 15. start_date > end_date Error
# -----------------------------------------------------------------------------
def test_start_date_greater_than_end_date_returns_422(client):
    """When start_date > end_date, return HTTP 422 error without swapping."""
    response = client.get("/api/dashboard?start_date=2026-09-25&end_date=2026-09-10")
    assert response.status_code == 422
    assert "cannot be greater than end_date" in response.json()["detail"]


# -----------------------------------------------------------------------------
# 17. Ensure Dashboard Uses Stored co2e Values (No Recalculation)
# -----------------------------------------------------------------------------
def test_dashboard_uses_stored_co2e_directly(client):
    """Ensure dashboard aggregates stored co2e and never calls calculate_co2e."""
    # Insert an activity with an arbitrary co2e value stored
    db = TestingSessionLocal()
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=date(2026, 9, 27), co2e=99.9))
    db.commit()
    db.close()

    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    # The dashboard must report the exact stored 99.9, proving it used the DB value directly
    assert data["total_co2"] == 99.9
    assert data["categories"]["food"]["co2e"] == 99.9
