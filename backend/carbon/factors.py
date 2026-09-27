"""Central, configurable PlanetPulse emission factors.

Factors are screening estimates in kg CO2e per configured unit. See
backend/DECISIONS.md for sources, geographic limits, and assumptions.
Override factors through the documented PLANETPULSE_FACTOR_* environment vars.
"""

from __future__ import annotations

import os


def _factor(name: str, default: float) -> float:
    try:
        value = float(os.getenv(f"PLANETPULSE_FACTOR_{name.upper()}", default))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Invalid emission factor configuration for {name}") from exc
    if value < 0:
        raise RuntimeError(f"Emission factor for {name} cannot be negative")
    return value


# Activity factors are category-specific; don't multiply by a generic category
# factor. Travel is passenger-km, electricity is kWh, food is one meal/serving.
FACTORS = {
    "travel": {
        "car": {"factor": _factor("CAR_PER_KM", 0.29), "unit": "km"},
        "metro": {"factor": _factor("METRO_PER_KM", 0.105), "unit": "km"},
        "bus": {"factor": _factor("BUS_PER_KM", 0.10), "unit": "km"},
        "bike": {"factor": _factor("BIKE_PER_KM", 0.0), "unit": "km"},
        "walk": {"factor": _factor("WALK_PER_KM", 0.0), "unit": "km"},
    },
    "electricity": {
        "default": {"factor": _factor("ELECTRICITY_PER_KWH", 0.716), "unit": "kwh", "kwh_per_hour": 0.5},
        "air conditioner": {"factor": _factor("ELECTRICITY_PER_KWH", 0.716), "unit": "kwh", "kwh_per_hour": 1.2},
        "ac": {"factor": _factor("ELECTRICITY_PER_KWH", 0.716), "unit": "kwh", "kwh_per_hour": 1.2},
        "lighting": {"factor": _factor("ELECTRICITY_PER_KWH", 0.716), "unit": "kwh", "kwh_per_hour": 0.08},
        "refrigerator": {"factor": _factor("ELECTRICITY_PER_KWH", 0.716), "unit": "kwh", "kwh_per_hour": 0.12},
        "other appliance": {"factor": _factor("ELECTRICITY_PER_KWH", 0.716), "unit": "kwh", "kwh_per_hour": 0.5},
    },
    "food": {
        "plant-based meal": {"factor": _factor("PLANT_MEAL", 0.5), "unit": "meal"},
        "chicken meal": {"factor": _factor("CHICKEN_MEAL", 1.5), "unit": "meal"},
        "dairy meal": {"factor": _factor("DAIRY_MEAL", 1.2), "unit": "meal"},
        "beef meal": {"factor": _factor("BEEF_MEAL", 5.0), "unit": "meal"},
        "chicken_meal": {"factor": _factor("CHICKEN_MEAL", 1.5), "unit": "meal"},
    },
}

# Emissions-free travel modes are valid and deliberately remain zero.
for _mode in ("bike", "walk"):
    if FACTORS["travel"][_mode]["factor"] < 0:
        raise RuntimeError(f"Invalid emission factor for {_mode}")
