"""Pydantic schemas for Dashboard API."""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class CategorySummary(BaseModel):
    """Emissions and activity count for a single category."""
    co2e: float = Field(0.0, description="Total CO2e emissions in kg CO2e")
    activities: int = Field(0, description="Total count of activities recorded")

    model_config = ConfigDict(from_attributes=True)


class DashboardCategories(BaseModel):
    """Categorical emission breakdown."""
    travel: CategorySummary = Field(default_factory=CategorySummary)
    electricity: CategorySummary = Field(default_factory=CategorySummary)
    food: CategorySummary = Field(default_factory=CategorySummary)

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    """Complete dashboard response model with frontend contract compatibility."""
    total_co2: float = Field(0.0, description="Overall total CO2e in kg CO2e")
    total_co2e: Optional[float] = Field(None, description="Total CO2e alias")
    total_activities: int = Field(0, description="Overall total activities recorded")
    activities: Optional[int] = Field(None, description="Activities count alias")
    categories: DashboardCategories = Field(default_factory=DashboardCategories)
    travel: Optional[float] = Field(None, description="Travel emissions in kg CO2e")
    travel_co2e: Optional[float] = Field(None, description="Travel emissions alias")
    electricity: Optional[float] = Field(None, description="Electricity emissions in kg CO2e")
    electricity_co2e: Optional[float] = Field(None, description="Electricity emissions alias")
    food: Optional[float] = Field(None, description="Food emissions in kg CO2e")
    food_co2e: Optional[float] = Field(None, description="Food emissions alias")
    reduction: Optional[float] = Field(0.0, description="Month-over-month reduction percentage")
    reduction_percent: Optional[float] = Field(0.0, description="Reduction percentage alias")
    category_totals: Optional[dict] = Field(default_factory=dict, description="Category emissions mapping")
    has_previous_month_data: bool = Field(False, description="Whether previous month data exists")
    current_month: Optional[dict] = Field(None, description="Current month summary")
    previous_month: Optional[dict] = Field(None, description="Previous month summary")
    goal: Optional[Any] = Field(None, description="Goal progress summary")
    goal_progress: Optional[Any] = Field(None, description="Goal progress alias")

    model_config = ConfigDict(from_attributes=True)
