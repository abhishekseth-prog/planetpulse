"""Pydantic schemas for Goal API."""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class GoalResponse(BaseModel):
    """Personal monthly carbon goal and progress tracking model (legacy contract)."""
    month: int = Field(..., ge=1, le=12, description="Target calendar month (1-12)")
    year: int = Field(..., description="Target calendar year")
    goal_co2e: float = Field(..., description="Configured monthly goal in kg CO2e")
    current_co2e: float = Field(..., description="Actual aggregated emissions in kg CO2e for the month")
    remaining_co2e: float = Field(..., description="Remaining emissions allowed before reaching goal (0 if exceeded)")
    over_goal_co2e: float = Field(..., description="Emissions exceeded beyond the goal (0 if within goal)")
    progress_percent: float = Field(..., ge=0.0, le=100.0, description="Progress percentage towards goal, capped at 100%")

    model_config = ConfigDict(from_attributes=True)


class MonthlyGoalUpdateRequest(BaseModel):
    """Payload schema for updating a user's monthly carbon goal target."""
    target: float = Field(..., ge=1.0, le=100000.0, description="Goal target in kg CO2e")

    @model_validator(mode="before")
    @classmethod
    def normalize_target_key(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "target" not in data:
                val = data.get("target_kg", data.get("target_co2e"))
                if val is not None:
                    data["target"] = val
        return data


class MonthlyGoalProgressResponse(BaseModel):
    """Frontend-compatible monthly goal and progress response schema."""
    target: float
    current: float
    progress: float
    remaining: float
    target_co2e: float
    used_co2e: float
    progress_percent: float
    remaining_co2e: float
    month: Optional[str] = None
