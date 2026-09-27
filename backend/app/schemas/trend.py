"""Pydantic schemas for Trend API."""

import datetime as dt
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class TrendPoint(BaseModel):
    """Aggregated carbon emissions and activity count for a single date."""
    date: dt.date = Field(..., description="Date of aggregated activities (YYYY-MM-DD)")
    co2e: float = Field(..., description="Total emissions on this date in kg CO2e")
    activities: int = Field(..., description="Number of activities recorded on this date")

    model_config = ConfigDict(from_attributes=True)


class TrendResponse(BaseModel):
    """Chronological trend response containing list of daily points."""
    trend: List[TrendPoint] = Field(
        default_factory=list,
        description="Chronologically sorted daily emissions data",
    )

    model_config = ConfigDict(from_attributes=True)
