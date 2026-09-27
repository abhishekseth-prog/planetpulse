from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.activity import ACTIVITY_ALIASES


class Scenario(BaseModel):
    activity: str = Field(..., description="Activity identifier (e.g., car, metro, bus)")
    amount: float = Field(..., gt=0, description="Numeric amount")
    unit: str = Field(..., description="Measurement unit (e.g., km, hours, meal)")

    @field_validator("activity")
    @classmethod
    def normalize_activity(cls, v: str) -> str:
        act = str(v).strip().lower()
        return ACTIVITY_ALIASES.get(act, act)

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, v: str) -> str:
        return str(v).strip().lower()


class WhatIfRequest(BaseModel):
    current: Optional[Scenario] = None
    alternative: Optional[Scenario] = None
    category: str = "travel"
    current_activity: Optional[str] = None
    alternative_activity: Optional[str] = None
    distance: Optional[float] = None
    amount: Optional[float] = None
    unit: str = "km"

    @model_validator(mode="before")
    @classmethod
    def normalize_scenarios(cls, data: Any) -> Any:
        if isinstance(data, dict):
            amt = data.get("amount", data.get("distance", 20.0))
            unt = data.get("unit", "km")
            
            if "current" not in data and data.get("current_activity"):
                data["current"] = {
                    "activity": data["current_activity"],
                    "amount": amt,
                    "unit": unt,
                }
            if "alternative" not in data and data.get("alternative_activity"):
                data["alternative"] = {
                    "activity": data["alternative_activity"],
                    "amount": amt,
                    "unit": unt,
                }
        return data

    @model_validator(mode="after")
    def ensure_both_scenarios(self):
        if self.current is None or self.alternative is None:
            raise ValueError("Both 'current' and 'alternative' scenarios are required.")
        return self


class WhatIfResponse(BaseModel):
    current_co2: float
    current_kg_co2e: float
    new_co2: float
    new_kg_co2e: float
    daily_reduction: float
    saving_kg_per_day: float
    monthly_reduction: float
    saving_kg_per_month: float
    reduction_percent: float
    is_reduction: bool
