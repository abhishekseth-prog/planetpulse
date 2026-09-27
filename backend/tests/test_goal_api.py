import pytest
import datetime as dt
from app.models.activity import Activity
from tests.conftest import client, TestingSessionLocal


# -----------------------------------------------------------------------------
# 1. Goal with No Activities
# -----------------------------------------------------------------------------
def test_goal_empty_database(client):
    """GET /api/goal with empty DB returns 0.0 current, 100.0 goal, 100.0 remaining, 0.0 progress."""
    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 9
    assert data["year"] == 2026
    assert data["goal_co2e"] == 100.0
    assert data["current_co2e"] == 0.0
    assert data["remaining_co2e"] == 100.0
    assert data["over_goal_co2e"] == 0.0
    assert data["progress_percent"] == 0.0


# -----------------------------------------------------------------------------
# 2. Goal with One Activity
# -----------------------------------------------------------------------------
def test_goal_single_activity(client):
    """Verify single activity calculation."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=20.0, unit="km", date=dt.date(2026, 9, 15), co2e=4.2))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 4.2
    assert pytest.approx(data["remaining_co2e"], rel=1e-4) == 95.8
    assert pytest.approx(data["progress_percent"], rel=1e-4) == 4.2
    assert data["over_goal_co2e"] == 0.0


# -----------------------------------------------------------------------------
# 3, 6, 7, 8. Multiple Activities in Same Month & Accurate Goal Calculation
# -----------------------------------------------------------------------------
def test_goal_multiple_activities_same_month(client):
    """Multiple activities in same month are summed correctly (40 kg CO2e -> 40% progress)."""
    db = TestingSessionLocal()
    # 20 + 20 = 40 kg CO2e
    db.add(Activity(category="travel", activity="car", amount=100.0, unit="km", date=dt.date(2026, 9, 5), co2e=20.0))
    db.add(Activity(category="travel", activity="car", amount=100.0, unit="km", date=dt.date(2026, 9, 20), co2e=20.0))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 40.0
    assert data["remaining_co2e"] == 60.0
    assert data["progress_percent"] == 40.0
    assert data["over_goal_co2e"] == 0.0


# -----------------------------------------------------------------------------
# 4. Activities from Another Month are Excluded
# -----------------------------------------------------------------------------
def test_goal_excludes_other_months(client):
    """Ensure activities from August and October are excluded from September."""
    db = TestingSessionLocal()
    # August (excluded)
    db.add(Activity(category="travel", activity="car", amount=50.0, unit="km", date=dt.date(2026, 8, 31), co2e=10.5))
    # September (included)
    db.add(Activity(category="travel", activity="car", amount=50.0, unit="km", date=dt.date(2026, 9, 15), co2e=10.5))
    # October (excluded)
    db.add(Activity(category="travel", activity="car", amount=50.0, unit="km", date=dt.date(2026, 10, 1), co2e=10.5))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 10.5
    assert data["remaining_co2e"] == 89.5


# -----------------------------------------------------------------------------
# 5. Activities from Another Year are Excluded
# -----------------------------------------------------------------------------
def test_goal_excludes_other_years(client):
    """Ensure September 2025 activity is not counted in September 2026."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=50.0, unit="km", date=dt.date(2025, 9, 15), co2e=10.5))
    db.add(Activity(category="travel", activity="car", amount=50.0, unit="km", date=dt.date(2026, 9, 15), co2e=15.0))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 15.0


# -----------------------------------------------------------------------------
# 9 & 10. Progress Capped at 100% & Over-Goal Calculation
# -----------------------------------------------------------------------------
def test_goal_progress_capped_and_over_goal_amount(client):
    """When monthly_co2e > goal (e.g. 125 kg CO2e), progress is capped at 100% and remaining is 0."""
    db = TestingSessionLocal()
    # Total = 125 kg CO2e against 100 kg goal
    db.add(Activity(category="travel", activity="flight", amount=500.0, unit="km", date=dt.date(2026, 9, 10), co2e=125.0))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 125.0
    assert data["progress_percent"] == 100.0
    assert data["remaining_co2e"] == 0.0
    assert data["over_goal_co2e"] == 25.0


# -----------------------------------------------------------------------------
# 11. Month = 1 (January Boundary)
# -----------------------------------------------------------------------------
def test_goal_january_boundary(client):
    """January boundary (2026-01-01 to 2026-01-31)."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2026, 1, 1), co2e=2.1))
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2026, 1, 31), co2e=2.1))
    # February 1st (excluded)
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2026, 2, 1), co2e=5.0))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=1&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 1
    assert pytest.approx(data["current_co2e"], rel=1e-4) == 4.2


# -----------------------------------------------------------------------------
# 12. Month = 12 (December Boundary)
# -----------------------------------------------------------------------------
def test_goal_december_boundary(client):
    """December boundary (2026-12-01 to 2026-12-31)."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2026, 12, 1), co2e=2.1))
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2026, 12, 31), co2e=2.1))
    # Next year January 1st (excluded)
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2027, 1, 1), co2e=5.0))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=12&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 12
    assert pytest.approx(data["current_co2e"], rel=1e-4) == 4.2


# -----------------------------------------------------------------------------
# 13. Leap-Year February Boundary
# -----------------------------------------------------------------------------
def test_goal_leap_year_february(client):
    """2024 is a leap year; February 29 must be included."""
    db = TestingSessionLocal()
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2024, 2, 29), co2e=2.1))
    # March 1 (excluded)
    db.add(Activity(category="travel", activity="car", amount=10.0, unit="km", date=dt.date(2024, 3, 1), co2e=5.0))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=2&year=2024")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 2.1


# -----------------------------------------------------------------------------
# 14, 15, 16. Validation Failures (Invalid Month & Year)
# -----------------------------------------------------------------------------
def test_invalid_month_zero(client):
    """month=0 returns HTTP 422."""
    response = client.get("/api/goal?month=0&year=2026")
    assert response.status_code == 422


def test_invalid_month_thirteen(client):
    """month=13 returns HTTP 422."""
    response = client.get("/api/goal?month=13&year=2026")
    assert response.status_code == 422


def test_invalid_year_too_low(client):
    """year=1800 returns HTTP 422."""
    response = client.get("/api/goal?month=9&year=1800")
    assert response.status_code == 422


def test_invalid_year_too_high(client):
    """year=3000 returns HTTP 422."""
    response = client.get("/api/goal?month=9&year=3000")
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 17. Explicit Month/Year Selection
# -----------------------------------------------------------------------------
def test_explicit_month_year(client):
    """Requesting specific month and year returns matching header fields."""
    response = client.get("/api/goal?month=5&year=2025")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 5
    assert data["year"] == 2025


# -----------------------------------------------------------------------------
# 18. No Parameters Uses Current Month/Year
# -----------------------------------------------------------------------------
def test_default_uses_current_month_year(client):
    """Calling /api/goal without parameters uses server's current month & year."""
    today = dt.date.today()
    response = client.get("/api/goal")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == today.month
    assert data["year"] == today.year


# -----------------------------------------------------------------------------
# 19. Only Month Uses Current Year
# -----------------------------------------------------------------------------
def test_only_month_uses_current_year(client):
    """Calling with only ?month=7 defaults year to current year."""
    today = dt.date.today()
    response = client.get("/api/goal?month=7")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 7
    assert data["year"] == today.year


# -----------------------------------------------------------------------------
# 20. Only Year Uses Current Month
# -----------------------------------------------------------------------------
def test_only_year_uses_current_month(client):
    """Calling with only ?year=2027 defaults month to current month."""
    today = dt.date.today()
    response = client.get("/api/goal?year=2027")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == today.month
    assert data["year"] == 2027


# -----------------------------------------------------------------------------
# 21 & 22. Stored co2e is Used Directly & Carbon Engine Not Called
# -----------------------------------------------------------------------------
def test_goal_uses_stored_co2e_directly(client):
    """Ensure goal aggregates stored co2e directly without calling calculate_co2e."""
    db = TestingSessionLocal()
    # Insert an activity with a distinct co2e stored value
    db.add(Activity(category="food", activity="chicken_meal", amount=1.0, unit="meal", date=dt.date(2026, 9, 27), co2e=77.7))
    db.commit()
    db.close()

    response = client.get("/api/goal?month=9&year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["current_co2e"] == 77.7
    assert data["remaining_co2e"] == 22.3
    assert data["progress_percent"] == 77.7
