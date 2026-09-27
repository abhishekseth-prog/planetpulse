"""Shared carbon engine used by activity logging and what-if simulation."""

from __future__ import annotations

import math

from carbon.factors import FACTORS


def calculate_carbon(category: str, value: float, activity: str | None = None, unit: str | None = None) -> float:
    """Return estimated kg CO2e using a centralized activity factor."""
    category_key = str(category or "").strip().lower()
    activity_key = str(activity or "default").strip().lower().replace("_", " ")
    if category_key not in FACTORS:
        raise ValueError(f"Unsupported category: {category}")
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Amount must be a number") from exc
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be greater than zero")

    category_factors = FACTORS[category_key]
    config = category_factors.get(activity_key)
    if config is None and category_key == "travel":
        raise ValueError(f"Unsupported travel activity: {activity}")
    config = config or category_factors.get("default")
    if config is None:
        raise ValueError(f"Unsupported {category_key} activity: {activity}")
    expected_unit = config["unit"]
    requested_unit = str(unit).strip().lower() if unit is not None else expected_unit
    if category_key == "electricity" and requested_unit == "hours":
        if amount > 24:
            raise ValueError("Electricity usage hours cannot exceed 24 per day")
        # Form accepts appliance hours as well as metered kWh. Hourly appliance
        # draw assumptions are centralized with the electricity factor.
        return round(amount * config["kwh_per_hour"] * config["factor"], 3)
    if requested_unit != expected_unit:
        raise ValueError(f"{category_key} activity must use {expected_unit}")
    return round(amount * config["factor"], 3)
