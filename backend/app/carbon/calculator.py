"""Carbon emission calculation engine.

Formula:
  CO2e = amount * emission_factor
"""

from typing import Any, Dict
from app.carbon.factors import (
    get_emission_factor,
    get_supported_activities,
    get_supported_units_for_activity,
)
from app.carbon.exceptions import (
    UnsupportedActivityError,
    UnsupportedUnitError,
    MissingFactorError,
    InvalidAmountError,
)


def calculate_co2e(
    activity: Any,
    amount: Any,
    unit: Any,
) -> float:
    """Calculate carbon emissions in kg CO2e for a given activity, amount, and unit.

    Args:
        activity: Name of the activity (e.g., 'car', 'ac', 'chicken_meal').
        amount: Positive numeric quantity.
        unit: Measurement unit (e.g., 'km', 'hours', 'meal').

    Returns:
        float: Calculated emissions in kg CO2e.

    Raises:
        InvalidAmountError: When amount is non-numeric or <= 0.
        UnsupportedActivityError: When activity is empty or not in factor registry.
        UnsupportedUnitError: When unit is empty or not supported for the activity.
        MissingFactorError: When factor lookup returns None for a valid activity/unit.
    """
    # 1. Validate Amount
    if amount is None or isinstance(amount, bool):
        raise InvalidAmountError("Amount is required and must be a valid number.")

    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError):
        raise InvalidAmountError(f"Amount must be a numeric value, received: {amount}")

    if numeric_amount <= 0:
        raise InvalidAmountError(f"Amount must be greater than 0, received: {amount}")

    # 2. Validate Activity
    if activity is None or not str(activity).strip():
        raise UnsupportedActivityError("Activity cannot be empty.")

    act_norm = str(activity).strip().lower()
    supported_acts = get_supported_activities()

    if act_norm not in supported_acts:
        raise UnsupportedActivityError(
            f"Unsupported activity '{activity}'. "
            f"Supported activities: {', '.join(supported_acts)}"
        )

    # 3. Validate Unit
    if unit is None or not str(unit).strip():
        raise UnsupportedUnitError("Unit cannot be empty.")

    unit_norm = str(unit).strip().lower()
    supported_units = get_supported_units_for_activity(act_norm)

    if unit_norm not in supported_units:
        raise UnsupportedUnitError(
            f"Unsupported unit '{unit}' for activity '{activity}'. "
            f"Supported units for '{activity}': {', '.join(supported_units)}"
        )

    # 4. Retrieve Emission Factor
    factor_obj = get_emission_factor(act_norm, unit_norm)
    if factor_obj is None:
        raise MissingFactorError(
            f"Emission factor configuration missing for activity '{activity}' with unit '{unit}'."
        )

    # 5. Calculate CO2e (kg CO2e)
    co2e = numeric_amount * factor_obj.factor
    return co2e


def calculate_co2e_detailed(
    activity: Any,
    amount: Any,
    unit: Any,
) -> Dict[str, Any]:
    """Calculate emissions and return detailed metadata including factor and source."""
    # Re-use validate and calculate
    co2e = calculate_co2e(activity, amount, unit)
    act_norm = str(activity).strip().lower()
    unit_norm = str(unit).strip().lower()
    factor_obj = get_emission_factor(act_norm, unit_norm)

    return {
        "activity": act_norm,
        "amount": float(amount),
        "unit": unit_norm,
        "emission_factor": factor_obj.factor if factor_obj else 0.0,
        "co2e": co2e,
        "co2e_unit": factor_obj.co2e_unit if factor_obj else "kg CO2e",
        "source": factor_obj.source if factor_obj else "",
        "assumptions": factor_obj.assumptions if factor_obj else "",
        "is_assumption": factor_obj.is_assumption if factor_obj else False,
    }
