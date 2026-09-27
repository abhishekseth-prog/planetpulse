"""Centralized Carbon Calculation Engine package."""

from app.carbon.factors import (
    EmissionFactor,
    EMISSION_FACTORS,
    get_emission_factor,
    get_supported_activities,
    get_supported_units_for_activity,
)
from app.carbon.exceptions import (
    CarbonEngineError,
    UnsupportedActivityError,
    UnsupportedUnitError,
    MissingFactorError,
    InvalidAmountError,
)
from app.carbon.calculator import calculate_co2e, calculate_co2e_detailed

__all__ = [
    "EmissionFactor",
    "EMISSION_FACTORS",
    "get_emission_factor",
    "get_supported_activities",
    "get_supported_units_for_activity",
    "CarbonEngineError",
    "UnsupportedActivityError",
    "UnsupportedUnitError",
    "MissingFactorError",
    "InvalidAmountError",
    "calculate_co2e",
    "calculate_co2e_detailed",
]
