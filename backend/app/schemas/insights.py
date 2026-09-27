from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InsightsResponse(BaseModel):
    """Personalized carbon reduction insights based on user activity."""
    largest_contributor: Optional[str] = None
    observation: Optional[str] = None
    recommendation: Optional[str] = None
    contribution_percent: float = 0.0
    opportunity: str
    actions: List[str] = Field(default_factory=list)
    potential_impact_kg: Optional[float] = 0.0
    period: str = "current_month"
    method: str = "rule_based"
    has_activities: bool = False
    has_emissions: bool = False
    activity_count: int = 0
    total_co2e: float = 0.0
    category_totals: Dict[str, float] = Field(default_factory=dict)
    recent_activities: List[Dict[str, Any]] = Field(default_factory=list)
    monthly_goal: Optional[Dict[str, Any]] = None
    monthly_reduction_percent: Optional[float] = None
    has_monthly_reduction_baseline: bool = False
    trend_7d: Optional[Dict[str, Any]] = None

