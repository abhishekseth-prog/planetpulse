import calendar
import datetime as dt
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.insights import InsightsResponse

from app.services.goal_service import get_monthly_goal_progress

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

    # 1. Monthly category breakdown
    query = db.query(Activity.category, func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= first_day, Activity.date <= last_day
    )
    count_query = db.query(func.count(Activity.id)).filter(
        Activity.date >= first_day, Activity.date <= last_day
    )
    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)
        count_query = count_query.filter(Activity.user_id == user_id)

    rows = query.group_by(Activity.category).all()
    breakdown = {cat: float(val) for cat, val in rows}

    travel_co2e = breakdown.get("travel", 0.0)
    electricity_co2e = breakdown.get("electricity", 0.0)
    food_co2e = breakdown.get("food", 0.0)
    total_co2e = round(travel_co2e + electricity_co2e + food_co2e, 4)
    activity_count = int(count_query.scalar() or 0)
    has_activities = activity_count > 0
    has_emissions = total_co2e > 0

    categories = {
        "travel": travel_co2e,
        "electricity": electricity_co2e,
        "food": food_co2e,
    }

    # 2. Monthly goal progress
    goal_data = get_monthly_goal_progress(db=db, user_id=user_id)
    goal_dict = goal_data.model_dump()

    # 3. 7-day trend
    six_days_ago = today - dt.timedelta(days=6)
    thirteen_days_ago = today - dt.timedelta(days=13)

    recent_trend_q = db.query(func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= six_days_ago, Activity.date <= today
    )
    prev_trend_q = db.query(func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= thirteen_days_ago, Activity.date < six_days_ago
    )
    if user_id is not None:
        recent_trend_q = recent_trend_q.filter(Activity.user_id == user_id)
        prev_trend_q = prev_trend_q.filter(Activity.user_id == user_id)

    recent_trend = float(recent_trend_q.scalar() or 0.0)
    previous_trend = float(prev_trend_q.scalar() or 0.0)
    trend_change = (
        round((recent_trend - previous_trend) / previous_trend * 100.0, 1)
        if previous_trend > 0
        else None
    )

    # 4. Previous month comparison
    first_prev = (first_day - dt.timedelta(days=1)).replace(day=1)
    last_prev = first_day - dt.timedelta(days=1)
    prev_month_q = db.query(func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= first_prev, Activity.date <= last_prev
    )
    if user_id is not None:
        prev_month_q = prev_month_q.filter(Activity.user_id == user_id)
    previous_month_total = float(prev_month_q.scalar() or 0.0)
    monthly_reduction = (
        round((previous_month_total - total_co2e) / previous_month_total * 100.0, 1)
        if previous_month_total > 0
        else None
    )

    # 5. Recent 5 activities
    recent_acts_q = db.query(Activity).order_by(Activity.date.desc(), Activity.id.desc())
    if user_id is not None:
        recent_acts_q = recent_acts_q.filter(Activity.user_id == user_id)
    recent_rows = recent_acts_q.limit(5).all()
    recent_activities = [
        {
            "category": a.category,
            "activity_type": a.activity,
            "activity_date": a.date.isoformat() if a.date else None,
            "co2e": round(float(a.co2e), 3),
        }
        for a in recent_rows
    ]

    trend_7d = {
        "current_period_co2e": round(recent_trend, 3),
        "previous_period_co2e": round(previous_trend, 3),
        "change_percent": trend_change,
        "has_baseline": previous_trend > 0,
    }

    if total_co2e <= 0:
        return InsightsResponse(
            largest_contributor="None",
            observation=None,
            recommendation="Start logging activities to get recommendations based on your footprint.",
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
            has_activities=has_activities,
            has_emissions=False,
            activity_count=activity_count,
            total_co2e=0.0,
            category_totals=categories,
            recent_activities=recent_activities,
            monthly_goal=goal_dict,
            monthly_reduction_percent=monthly_reduction,
            has_monthly_reduction_baseline=previous_month_total > 0,
            trend_7d=trend_7d,
        )

    top_cat = max(categories, key=categories.get)
    top_val = categories[top_cat]
    share = round(top_val / total_co2e * 100.0, 1)
    potential = round(top_val * 0.10, 1)

    rec = RECOMMENDATIONS.get(top_cat, RECOMMENDATIONS["travel"])
    opportunity_text = (
        f"{rec['opportunity']} A 10% reduction in {rec['name'].lower()} "
        f"could avoid about {potential:g} kg CO2e this month."
    )

    return InsightsResponse(
        largest_contributor=rec["name"],
        observation=f"{rec['name']} is currently your largest emission category.",
        recommendation=rec["opportunity"],
        contribution_percent=share,
        opportunity=opportunity_text,
        actions=rec["actions"],
        potential_impact_kg=potential,
        period="current_month",
        method="rule_based",
        has_activities=has_activities,
        has_emissions=True,
        activity_count=activity_count,
        total_co2e=total_co2e,
        category_totals=categories,
        recent_activities=recent_activities,
        monthly_goal=goal_dict,
        monthly_reduction_percent=monthly_reduction,
        has_monthly_reduction_baseline=previous_month_total > 0,
        trend_7d=trend_7d,
    )
