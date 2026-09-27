"""Exceptions for the Carbon Calculation Engine."""


class CarbonEngineError(Exception):
    """Base exception for all Carbon Engine errors."""
    pass


class UnsupportedActivityError(CarbonEngineError):
    """Raised when an activity is not recognized by the engine."""
    pass


class UnsupportedUnitError(CarbonEngineError):
    """Raised when a unit is not recognized or not applicable to the activity."""
    pass


class MissingFactorError(CarbonEngineError):
    """Raised when an emission factor configuration is missing for a valid activity/unit pair."""
    pass


class InvalidAmountError(CarbonEngineError):
    """Raised when the provided activity amount is non-positive or non-numeric."""
    pass
