import pytest
from datetime import date
from app.models.activity import Activity
from app.carbon.exceptions import CarbonEngineError
from tests.conftest import client, TestingSessionLocal


# -----------------------------------------------------------------------------
# 1. Successful Car Activity
# -----------------------------------------------------------------------------
def test_create_car_activity(client):
    """POST /api/activities with car travel returns 201 and co2e 4.2."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["id"] > 0
    assert data["category"] == "travel"
    assert data["activity"] == "car"
    assert data["amount"] == 20.0
    assert data["unit"] == "km"
    assert data["date"] == "2026-09-27"
    assert pytest.approx(data["co2e"], rel=1e-4) == 4.2


# -----------------------------------------------------------------------------
# 2. Successful Electricity Activity
# -----------------------------------------------------------------------------
def test_create_electricity_activity(client):
    """POST /api/activities with AC electricity returns 201 and co2e 3.375."""
    payload = {
        "category": "electricity",
        "activity": "ac",
        "amount": 5,
        "unit": "hours",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "electricity"
    assert data["activity"] == "ac"
    assert data["amount"] == 5.0
    assert data["unit"] == "hours"
    assert pytest.approx(data["co2e"], rel=1e-4) == 3.375


# -----------------------------------------------------------------------------
# 3. Successful Food Activity
# -----------------------------------------------------------------------------
def test_create_food_activity(client):
    """POST /api/activities with chicken meal returns 201 and co2e 1.8."""
    payload = {
        "category": "food",
        "activity": "chicken_meal",
        "amount": 1,
        "unit": "meal",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "food"
    assert data["activity"] == "chicken_meal"
    assert data["amount"] == 1.0
    assert data["unit"] == "meal"
    assert pytest.approx(data["co2e"], rel=1e-4) == 1.8


# -----------------------------------------------------------------------------
# 4. Correct CO2e Returned
# -----------------------------------------------------------------------------
def test_correct_co2e_calculation_verified(client):
    """Verify response co2e matches pure Carbon Engine value (e.g. 50 km metro)."""
    payload = {
        "category": "travel",
        "activity": "metro",
        "amount": 50,
        "unit": "km",
        "date": "2026-09-27",
    }
    # 50 km * 0.03 kg CO2e/km = 1.5 kg CO2e
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 201
    assert pytest.approx(response.json()["co2e"], rel=1e-4) == 1.5


# -----------------------------------------------------------------------------
# 5. Activity Persisted in Database
# -----------------------------------------------------------------------------
def test_activity_persisted_in_database(client):
    """Verify that recorded activity exists in the SQLite database."""
    payload = {
        "category": "travel",
        "activity": "bus",
        "amount": 10,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 201
    activity_id = response.json()["id"]

    # Verify directly in SQLite test session
    db = TestingSessionLocal()
    saved = db.query(Activity).filter_by(id=activity_id).first()
    assert saved is not None
    assert saved.category == "travel"
    assert saved.activity == "bus"
    assert saved.amount == 10.0
    assert saved.unit == "km"
    assert saved.co2e == 1.0  # 10 * 0.10
    db.close()


# -----------------------------------------------------------------------------
# 6. Invalid Category
# -----------------------------------------------------------------------------
def test_invalid_category_rejected(client):
    """Reject requests with unsupported category (HTTP 422)."""
    payload = {
        "category": "aerospace",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422
    assert "Unsupported category" in response.text


# -----------------------------------------------------------------------------
# 7. Invalid Activity
# -----------------------------------------------------------------------------
def test_invalid_activity_rejected(client):
    """Reject requests with unsupported activity (HTTP 422)."""
    payload = {
        "category": "travel",
        "activity": "teleportation",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422
    assert "Unsupported activity" in response.text


# -----------------------------------------------------------------------------
# 8. Invalid Amount (Non-numeric)
# -----------------------------------------------------------------------------
def test_invalid_amount_non_numeric_rejected(client):
    """Reject requests with non-numeric amount (HTTP 422)."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": "ten_kilometers",
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 9. Zero Amount
# -----------------------------------------------------------------------------
def test_zero_amount_rejected(client):
    """Reject requests with amount = 0 (HTTP 422)."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 0,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422
    assert "Amount must be greater than 0" in response.text


# -----------------------------------------------------------------------------
# 10. Negative Amount
# -----------------------------------------------------------------------------
def test_negative_amount_rejected(client):
    """Reject requests with negative amount (HTTP 422)."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": -5.5,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422
    assert "Amount must be greater than 0" in response.text


# -----------------------------------------------------------------------------
# 11. Invalid Unit
# -----------------------------------------------------------------------------
def test_invalid_unit_rejected(client):
    """Reject requests with unsupported unit (HTTP 422)."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "gallons",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422
    assert "Unsupported unit" in response.text


# -----------------------------------------------------------------------------
# 12. Invalid Date
# -----------------------------------------------------------------------------
def test_invalid_date_rejected(client):
    """Reject requests with malformed date format (HTTP 422)."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "27-09-2026",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422


# -----------------------------------------------------------------------------
# 13. Validation Failure Does Not Create Database Record
# -----------------------------------------------------------------------------
def test_validation_failure_does_not_persist(client):
    """Ensure invalid submissions do not insert records into the database."""
    db = TestingSessionLocal()
    initial_count = db.query(Activity).count()
    db.close()

    payload = {
        "category": "travel",
        "activity": "car",
        "amount": -50,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 422

    db = TestingSessionLocal()
    final_count = db.query(Activity).count()
    db.close()
    assert final_count == initial_count


# -----------------------------------------------------------------------------
# 14. Carbon Engine Errors Handled Gracefully (HTTP 400)
# -----------------------------------------------------------------------------
def test_carbon_engine_error_returns_400(client, monkeypatch):
    """If Carbon Engine raises a domain error, API returns HTTP 400 Bad Request."""
    import app.services.activity_service as act_service

    def mock_calc(*args, **kwargs):
        raise CarbonEngineError("Simulated carbon engine domain error")

    monkeypatch.setattr(act_service, "calculate_co2e", mock_calc)

    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    response = client.post("/api/activities", json=payload)
    assert response.status_code == 400
    assert "Simulated carbon engine domain error" in response.json()["detail"]
