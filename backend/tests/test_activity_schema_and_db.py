import pytest
from datetime import date
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.schemas.activity import ActivityCreate
from app.models.activity import Activity
from app.database.session import Base


# ---------------------------------------------------------
# 1. Valid Activity Data Tests
# ---------------------------------------------------------
def test_valid_travel_activity():
    """Verify valid travel activity parsing and schema instantiation."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    obj = ActivityCreate(**payload)
    assert obj.category == "travel"
    assert obj.activity == "car"
    assert obj.amount == 20.0
    assert obj.unit == "km"
    assert obj.date == date(2026, 9, 27)


def test_valid_electricity_activity():
    """Verify valid electricity activity parsing."""
    payload = {
        "category": "electricity",
        "activity": "ac",
        "amount": 5,
        "unit": "hours",
        "date": "2026-09-27",
    }
    obj = ActivityCreate(**payload)
    assert obj.category == "electricity"
    assert obj.activity == "ac"
    assert obj.amount == 5.0
    assert obj.unit == "hours"
    assert obj.date == date(2026, 9, 27)


def test_valid_food_activity():
    """Verify valid food activity parsing."""
    payload = {
        "category": "food",
        "activity": "chicken_meal",
        "amount": 1,
        "unit": "meal",
        "date": "2026-09-27",
    }
    obj = ActivityCreate(**payload)
    assert obj.category == "food"
    assert obj.activity == "chicken_meal"
    assert obj.amount == 1.0
    assert obj.unit == "meal"
    assert obj.date == date(2026, 9, 27)


# ---------------------------------------------------------
# 2. Missing Category Tests
# ---------------------------------------------------------
def test_missing_category():
    """Reject when category field is missing."""
    payload = {
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    errors = str(exc_info.value)
    assert "category" in errors


def test_empty_category():
    """Reject when category is empty or whitespace."""
    payload = {
        "category": "   ",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Category cannot be empty" in str(exc_info.value)


# ---------------------------------------------------------
# 3. Invalid Category Tests
# ---------------------------------------------------------
def test_invalid_category():
    """Reject unsupported category."""
    payload = {
        "category": "space_travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Unsupported category" in str(exc_info.value)


# ---------------------------------------------------------
# 4. Missing Activity Tests
# ---------------------------------------------------------
def test_missing_activity():
    """Reject when activity field is missing."""
    payload = {
        "category": "travel",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "activity" in str(exc_info.value)


def test_empty_activity():
    """Reject when activity is empty or whitespace."""
    payload = {
        "category": "travel",
        "activity": "  ",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Activity cannot be empty" in str(exc_info.value)


def test_unsupported_activity_for_category():
    """Reject activity incompatible with category."""
    payload = {
        "category": "travel",
        "activity": "chicken_meal",
        "amount": 20,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "not supported under category 'travel'" in str(exc_info.value)


# ---------------------------------------------------------
# 5. Missing Amount Tests
# ---------------------------------------------------------
def test_missing_amount():
    """Reject when amount field is missing."""
    payload = {
        "category": "travel",
        "activity": "car",
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "amount" in str(exc_info.value)


# ---------------------------------------------------------
# 6. Zero Amount Tests
# ---------------------------------------------------------
def test_zero_amount():
    """Reject when amount is zero."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 0,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Amount must be greater than 0" in str(exc_info.value)


# ---------------------------------------------------------
# 7. Negative Amount Tests
# ---------------------------------------------------------
def test_negative_amount():
    """Reject when amount is negative."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": -15.5,
        "unit": "km",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Amount must be greater than 0" in str(exc_info.value)


# ---------------------------------------------------------
# 8. Invalid Unit Tests
# ---------------------------------------------------------
def test_unsupported_unit():
    """Reject unknown / unsupported unit."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "lightyears",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Unsupported unit" in str(exc_info.value)


def test_mismatched_category_unit():
    """Reject unit that belongs to a different category."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "meal",
        "date": "2026-09-27",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "Unit 'meal' is not supported under category 'travel'" in str(exc_info.value)


# ---------------------------------------------------------
# 9. Invalid Date Tests
# ---------------------------------------------------------
def test_invalid_date_format():
    """Reject date that does not conform to valid ISO calendar date."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "not-a-date",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "date" in str(exc_info.value)


def test_invalid_calendar_date():
    """Reject invalid calendar dates like 2026-02-30."""
    payload = {
        "category": "travel",
        "activity": "car",
        "amount": 20,
        "unit": "km",
        "date": "2026-02-30",
    }
    with pytest.raises(ValidationError) as exc_info:
        ActivityCreate(**payload)
    assert "date" in str(exc_info.value)


# ---------------------------------------------------------
# 10. Database Connection & Model Creation Tests
# ---------------------------------------------------------
def test_database_model_creation_and_persistence():
    """Verify Activity SQLAlchemy model creation and SQLite persistence."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()

    activity_record = Activity(
        category="travel",
        activity="car",
        amount=25.5,
        unit="km",
        date=date(2026, 9, 27),
    )

    session.add(activity_record)
    session.commit()
    session.refresh(activity_record)

    assert activity_record.id is not None
    assert activity_record.id > 0
    assert activity_record.category == "travel"
    assert activity_record.activity == "car"
    assert activity_record.amount == 25.5
    assert activity_record.unit == "km"
    assert activity_record.date == date(2026, 9, 27)
    assert activity_record.created_at is not None

    # Query back
    queried = session.query(Activity).filter_by(id=activity_record.id).first()
    assert queried is not None
    assert queried.activity == "car"
    assert "<Activity(id=1" in repr(queried)

    session.close()
