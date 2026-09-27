import calendar
import datetime as dt
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.insights import InsightsResponse

RECOMMENDATIONS = {
    "travel": {
        "name": "Travel",
        "opportunity": "Replacing short car trips with public transit or active travel is your clearest opportunity.",
        "actions": [
            "Replace 2 short car trips with metro, bus, or cycling",
            "Combine nearby errands into a single journey",
            "Choose a lower-impact commute option once this week",
        ],
    },
    "electricity": {
        "name": "Electricity",
        "opportunity": "Reducing appliance runtime, especially cooling and heating, is your clearest opportunity.",
        "actions": [
            "Reduce AC or space heater use by 1 hour a day",
            "Switch off appliances at the socket when idle",
            "Use efficient settings on high-power appliances",
        ],
    },
    "food": {
        "name": "Food",
        "opportunity": "Choosing lower-impact meals is your clearest opportunity.",
        "actions": [
            "Choose 1 lower-impact meal this week",
            "Try a plant-based swap for one meal",
            "Plan portions to minimize food waste",
        ],
    },
}


def get_insights(db: Session, user_id: Optional[int] = None) -> InsightsResponse:
    """Generate deterministic rule-based insights and recommendations based on current month emissions."""
    today = dt.date.today()
    first_day = dt.date(today.year, today.month, 1)
    _, last_day_num = calendar.monthrange(today.year, today.month)
    last_day = dt.date(today.year, today.month, last_day_num)

    query = db.query(Activity.category, func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= first_day, Activity.date <= last_day
    )
    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)

    rows = query.group_by(Activity.category).all()
    breakdown = {cat: float(val) for cat, val in rows}

    travel_co2e = breakdown.get("travel", 0.0)
    electricity_co2e = breakdown.get("electricity", 0.0)
    food_co2e = breakdown.get("food", 0.0)
    total_co2e = travel_co2e + electricity_co2e + food_co2e

    if total_co2e <= 0:
        return InsightsResponse(
            largest_contributor="None",
            contribution_percent=0.0,
            opportunity="Start logging activities to get recommendations based on your footprint.",
            actions=[
                "Log your daily travel",
                "Record electricity and appliance usage",
                "Track your meals",
            ],
            potential_impact_kg=0.0,
            period="current_month",
            method="rule_based",
        )

    categories = {
        "travel": travel_co2e,
        "electricity": electricity_co2e,
        "food": food_co2e,
    }
    top_cat = max(categories, key=categories.get)
    top_val = categories[top_cat]
    share = round(top_val / total_co2e * 100, 1)
    potential = round(top_val * 0.10, 1)

    rec = RECOMMENDATIONS.get(top_cat, RECOMMENDATIONS["travel"])
    opportunity_text = (
        f"{rec['opportunity']} A 10% reduction in {rec['name'].lower()} "
        f"could avoid about {potential:g} kg CO2e this month."
    )

    return InsightsResponse(
        largest_contributor=rec["name"],
        contribution_percent=share,
        opportunity=opportunity_text,
        actions=rec["actions"],
        potential_impact_kg=potential,
        period="current_month",
        method="rule_based",
    )
