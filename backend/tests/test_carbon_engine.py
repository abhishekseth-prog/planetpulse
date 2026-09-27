import pytest
from app.carbon import (
    calculate_co2e,
    calculate_co2e_detailed,
    get_emission_factor,
    EMISSION_FACTORS,
    EmissionFactor,
    UnsupportedActivityError,
    UnsupportedUnitError,
    MissingFactorError,
    InvalidAmountError,
)


# -----------------------------------------------------------------------------
# 1. Valid Car Calculation
# -----------------------------------------------------------------------------
def test_valid_car_calculation():
    """Verify car calculation: 20 km at 0.21 kg CO2e/km yields 4.2 kg CO2e."""
    co2e = calculate_co2e(activity="car", amount=20, unit="km")
    assert pytest.approx(co2e, rel=1e-5) == 4.2


# -----------------------------------------------------------------------------
# 2. Valid AC Calculation
# -----------------------------------------------------------------------------
def test_valid_ac_calculation():
    """Verify AC calculation: 5 hours at 0.675 kg CO2e/hour yields 3.375 kg CO2e."""
    co2e = calculate_co2e(activity="ac", amount=5, unit="hours")
    assert pytest.approx(co2e, rel=1e-5) == 3.375


# -----------------------------------------------------------------------------
# 3. Valid Food Calculation
# -----------------------------------------------------------------------------
def test_valid_food_calculation():
    """Verify food calculation: 1 chicken_meal at 1.8 kg CO2e/meal yields 1.8 kg CO2e."""
    co2e = calculate_co2e(activity="chicken_meal", amount=1, unit="meal")
    assert pytest.approx(co2e, rel=1e-5) == 1.8


# -----------------------------------------------------------------------------
# 4. Correct Amount × Factor Calculation
# -----------------------------------------------------------------------------
def test_amount_times_factor_accuracy():
    """Verify precision for various activities matches amount * factor exactly."""
    activities_to_test = [
        ("bus", 15.0, "km", 0.10, 1.5),
        ("metro", 30.0, "km", 0.03, 0.9),
        ("beef_meal", 2.0, "meal", 6.5, 13.0),
        ("vegan_meal", 3.0, "meal", 0.5, 1.5),
        ("bike", 10.0, "km", 0.0, 0.0),
        ("walk", 5.0, "km", 0.0, 0.0),
        ("ac", 10.0, "kwh", 0.45, 4.5),
    ]

    for activity, amount, unit, expected_factor, expected_co2e in activities_to_test:
        factor_obj = get_emission_factor(activity, unit)
        assert factor_obj is not None
        assert factor_obj.factor == expected_factor
        result = calculate_co2e(activity, amount, unit)
        assert pytest.approx(result, rel=1e-5) == expected_co2e


def test_detailed_metadata_result():
    """Verify calculate_co2e_detailed returns complete calculation audit data."""
    details = calculate_co2e_detailed(activity="car", amount=20, unit="km")
    assert details["activity"] == "car"
    assert details["amount"] == 20.0
    assert details["unit"] == "km"
    assert details["emission_factor"] == 0.21
    assert details["co2e"] == 4.2
    assert details["co2e_unit"] == "kg CO2e"
    assert "DEFRA" in details["source"]
    assert details["is_assumption"] is False


# -----------------------------------------------------------------------------
# 5. Unsupported Activity
# -----------------------------------------------------------------------------
def test_unsupported_activity():
    """Reject unknown or unsupported activity name."""
    with pytest.raises(UnsupportedActivityError) as exc_info:
        calculate_co2e(activity="rocket_ship", amount=10, unit="km")
    assert "Unsupported activity 'rocket_ship'" in str(exc_info.value)


def test_empty_activity():
    """Reject empty or whitespace activity."""
    with pytest.raises(UnsupportedActivityError) as exc_info:
        calculate_co2e(activity="   ", amount=10, unit="km")
    assert "Activity cannot be empty" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 6. Unsupported Unit
# -----------------------------------------------------------------------------
def test_unsupported_unit():
    """Reject unsupported unit for an activity."""
    with pytest.raises(UnsupportedUnitError) as exc_info:
        calculate_co2e(activity="car", amount=10, unit="liters")
    assert "Unsupported unit 'liters' for activity 'car'" in str(exc_info.value)


def test_empty_unit():
    """Reject empty or whitespace unit."""
    with pytest.raises(UnsupportedUnitError) as exc_info:
        calculate_co2e(activity="car", amount=10, unit="  ")
    assert "Unit cannot be empty" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 7. Invalid Amount
# -----------------------------------------------------------------------------
def test_invalid_amount_non_numeric():
    """Reject non-numeric amount values."""
    with pytest.raises(InvalidAmountError) as exc_info:
        calculate_co2e(activity="car", amount="not-a-number", unit="km")
    assert "Amount must be a numeric value" in str(exc_info.value)


def test_invalid_amount_boolean():
    """Reject boolean values as amount."""
    with pytest.raises(InvalidAmountError) as exc_info:
        calculate_co2e(activity="car", amount=True, unit="km")
    assert "Amount is required and must be a valid number" in str(exc_info.value)


def test_invalid_amount_none():
    """Reject None as amount."""
    with pytest.raises(InvalidAmountError) as exc_info:
        calculate_co2e(activity="car", amount=None, unit="km")
    assert "Amount is required" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 8. Zero Amount
# -----------------------------------------------------------------------------
def test_zero_amount():
    """Reject amount of zero."""
    with pytest.raises(InvalidAmountError) as exc_info:
        calculate_co2e(activity="car", amount=0, unit="km")
    assert "Amount must be greater than 0" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 9. Negative Amount
# -----------------------------------------------------------------------------
def test_negative_amount():
    """Reject negative amounts."""
    with pytest.raises(InvalidAmountError) as exc_info:
        calculate_co2e(activity="car", amount=-10.5, unit="km")
    assert "Amount must be greater than 0" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 10. Missing Emission Factor
# -----------------------------------------------------------------------------
def test_missing_emission_factor(monkeypatch):
    """Raise MissingFactorError if a valid activity/unit pair has no factor in registry."""
    monkeypatch.setattr(
        "app.carbon.calculator.get_emission_factor",
        lambda act, u: None,
    )
    with pytest.raises(MissingFactorError) as exc_info:
        calculate_co2e(activity="car", amount=10, unit="km")
    assert "Emission factor configuration missing" in str(exc_info.value)
