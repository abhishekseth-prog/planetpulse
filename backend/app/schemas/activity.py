import datetime as dt
from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

SUPPORTED_CATEGORIES: Set[str] = {"travel", "electricity", "food"}

CATEGORY_ACTIVITIES: Dict[str, Set[str]] = {
    "travel": {"car", "bus", "train", "metro", "flight", "plane", "bike", "walk", "motorcycle"},
    "electricity": {"ac", "fan", "heater", "lighting", "refrigerator", "computer", "tv", "appliances"},
    "food": {"chicken_meal", "beef_meal", "vegetarian_meal", "vegan_meal", "fish_meal", "dairy"},
}

CATEGORY_UNITS: Dict[str, Set[str]] = {
    "travel": {"km", "miles"},
    "electricity": {"hours", "kwh"},
    "food": {"meal", "servings", "kg"},
}

ACTIVITY_ALIASES: Dict[str, str] = {
    "air conditioner": "ac",
    "air_conditioner": "ac",
    "chicken meal": "chicken_meal",
    "beef meal": "beef_meal",
    "fish meal": "fish_meal",
    "vegetarian meal": "vegetarian_meal",
    "veg_meal": "vegetarian_meal",
    "vegan meal": "vegan_meal",
    "plant-based meal": "vegan_meal",
    "plant_based_meal": "vegan_meal",
    "plant based meal": "vegan_meal",
    "dairy meal": "dairy",
    "dairy_meal": "dairy",
    "other appliance": "appliances",
    "other_appliance": "appliances",
    "appliance": "appliances",
}

ALL_SUPPORTED_ACTIVITIES: Set[str] = {
    activity for acts in CATEGORY_ACTIVITIES.values() for activity in acts
}

ALL_SUPPORTED_UNITS: Set[str] = {
    unit for units in CATEGORY_UNITS.values() for unit in units
}


class ActivityBase(BaseModel):
    """Base schema for an activity with core validation rules and frontend alias support."""
    category: str = Field(..., description="Activity category (travel, electricity, food)")
    activity: str = Field(..., description="Specific activity identifier (e.g., car, ac, chicken_meal)")
    amount: float = Field(..., description="Numeric measurement value (> 0)")
    unit: str = Field(..., description="Unit of measurement (e.g., km, hours, meal)")
    date: dt.date = Field(..., description="Date of activity in YYYY-MM-DD format")

    @model_validator(mode="before")
    @classmethod
    def pre_normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Map legacy frontend alias keys if canonical keys are not provided
            if "activity" not in data and "activity_type" in data:
                data["activity"] = data["activity_type"]
            if "amount" not in data and "value" in data:
                data["amount"] = data["value"]
            if "date" not in data and "activity_date" in data:
                data["date"] = data["activity_date"]
            # Activity alias normalizations
            act = data.get("activity")
            if isinstance(act, str):
                act_clean = act.strip().lower()
                if act_clean in ACTIVITY_ALIASES:
                    data["activity"] = ACTIVITY_ALIASES[act_clean]
        return data

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("Category cannot be empty")
        normalized = str(v).strip().lower()
        if normalized not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category '{v}'. Supported categories: {', '.join(sorted(SUPPORTED_CATEGORIES))}"
            )
        return normalized

    @field_validator("activity")
    @classmethod
    def validate_activity(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("Activity cannot be empty")
        normalized = str(v).strip().lower()
        if normalized in ACTIVITY_ALIASES:
            normalized = ACTIVITY_ALIASES[normalized]
        if normalized not in ALL_SUPPORTED_ACTIVITIES:
            raise ValueError(
                f"Unsupported activity '{v}'. Supported activities: {', '.join(sorted(ALL_SUPPORTED_ACTIVITIES))}"
            )
        return normalized

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v is None:
            raise ValueError("Amount is required")
        if v <= 0:
            raise ValueError(f"Amount must be greater than 0, received: {v}")
        return float(v)

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        if v is None or not str(v).strip():
            raise ValueError("Unit cannot be empty")
        normalized = str(v).strip().lower()
        if normalized not in ALL_SUPPORTED_UNITS:
            raise ValueError(
                f"Unsupported unit '{v}'. Supported units: {', '.join(sorted(ALL_SUPPORTED_UNITS))}"
            )
        return normalized

    @model_validator(mode="after")
    def validate_cross_field_compatibility(self):
        # Validate that activity is valid for the specified category
        if self.category in CATEGORY_ACTIVITIES:
            allowed_acts = CATEGORY_ACTIVITIES[self.category]
            if self.activity not in allowed_acts:
                raise ValueError(
                    f"Activity '{self.activity}' is not supported under category '{self.category}'. "
                    f"Allowed activities: {', '.join(sorted(allowed_acts))}"
                )

        # Validate that unit is valid for the specified category
        if self.category in CATEGORY_UNITS:
            allowed_units = CATEGORY_UNITS[self.category]
            if self.unit not in allowed_units:
                raise ValueError(
                    f"Unit '{self.unit}' is not supported under category '{self.category}'. "
                    f"Allowed units: {', '.join(sorted(allowed_units))}"
                )
        return self


class ActivityCreate(ActivityBase):
    """Input payload schema for creating an activity."""
    pass


class ActivityResponse(ActivityBase):
    """Response schema for an activity stored in the database with frontend compatibility."""
    id: int
    user_id: Optional[int] = None
    co2e: float
    created_at: dt.datetime

    # Explicitly serialized frontend compatibility computed fields
    @computed_field
    @property
    def activity_id(self) -> int:
        return self.id

    @computed_field
    @property
    def activity_type(self) -> str:
        return self.activity

    @computed_field
    @property
    def value(self) -> float:
        return self.amount

    @computed_field
    @property
    def activity_date(self) -> str:
        return self.date.isoformat()

    @computed_field
    @property
    def carbon_kg_co2e(self) -> float:
        return self.co2e

    model_config = ConfigDict(from_attributes=True)
