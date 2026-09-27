from typing import List
from pydantic import BaseModel


class InsightsResponse(BaseModel):
    """Personalized carbon reduction insights based on user activity."""
    largest_contributor: str
    contribution_percent: float
    opportunity: str
    actions: List[str]
    potential_impact_kg: float
    period: str = "current_month"
    method: str = "rule_based"
