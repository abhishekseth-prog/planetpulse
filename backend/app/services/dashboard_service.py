"""Dashboard aggregation service.

CRITICAL: Aggregates stored Activity.co2e from SQLite directly.
Does NOT invoke calculate_co2e or recalculate emission factors.
"""

import calendar
import datetime as dt
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.schemas.dashboard import (
    CategorySummary,
    DashboardCategories,
    DashboardResponse,
)
from app.services.goal_service import get_monthly_goal_progress


def get_dashboard_summary(
    db: Session,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    user_id: Optional[int] = None,
) -> DashboardResponse:
    """Aggregate stored activities to compute dashboard totals, category breakdown, and goal progress.

    Args:
        db: Active SQLAlchemy database session.
        start_date: Optional start date filter (inclusive).
        end_date: Optional end date filter (inclusive).
        user_id: Optional user ID for account scoping.

    Returns:
        DashboardResponse: Structured response with overall, category totals, and aliases.
    """
    filters = []
    if user_id is not None:
        filters.append(Activity.user_id == user_id)
    if start_date is not None:
        filters.append(Activity.date >= start_date)
    if end_date is not None:
        filters.append(Activity.date <= end_date)

    # 1. Overall Aggregation: SUM(co2e) and COUNT(id)
    overall_query = db.query(
        func.coalesce(func.sum(Activity.co2e), 0.0).label("total_co2"),
        func.count(Activity.id).label("total_activities"),
    )
    if filters:
        overall_query = overall_query.filter(*filters)

    overall_row = overall_query.first()
    total_co2 = float(overall_row.total_co2) if overall_row and overall_row.total_co2 is not None else 0.0
    total_activities = int(overall_row.total_activities) if overall_row and overall_row.total_activities is not None else 0

    # 2. Category Aggregation: GROUP BY category
    cat_query = db.query(
        Activity.category,
        func.coalesce(func.sum(Activity.co2e), 0.0).label("cat_co2"),
        func.count(Activity.id).label("cat_count"),
    )
    if filters:
        cat_query = cat_query.filter(*filters)

    cat_rows = cat_query.group_by(Activity.category).all()

    category_map = {
        "travel": CategorySummary(co2e=0.0, activities=0),
        "electricity": CategorySummary(co2e=0.0, activities=0),
        "food": CategorySummary(co2e=0.0, activities=0),
    }

    for row in cat_rows:
        cat_name = str(row.category).strip().lower()
        if cat_name in category_map:
            category_map[cat_name] = CategorySummary(
                co2e=round(float(row.cat_co2), 4),
                activities=int(row.cat_count),
            )

    travel_val = category_map["travel"].co2e
    elec_val = category_map["electricity"].co2e
    food_val = category_map["food"].co2e

    # 3. Calculate month-over-month reduction if no explicit date filters
    today = dt.date.today()
    reduction = 0.0
    if start_date is None and end_date is None:
        # Current month
        first_current = dt.date(today.year, today.month, 1)
        # Previous month
        first_prev = (first_current - dt.timedelta(days=1)).replace(day=1)
        last_prev = first_current - dt.timedelta(days=1)
        
        prev_q = db.query(func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
            Activity.date >= first_prev, Activity.date <= last_prev
        )
        if user_id is not None:
            prev_q = prev_q.filter(Activity.user_id == user_id)
        prev_total = float(prev_q.scalar())
        if prev_total > 0:
            reduction = round((prev_total - total_co2) / prev_total * 100.0, 1)

    # 4. Fetch goal progress
    goal_data = get_monthly_goal_progress(db=db, user_id=user_id)
    goal_dict = goal_data.model_dump()

    return DashboardResponse(
        total_co2=round(total_co2, 4),
        total_co2e=round(total_co2, 4),
        total_activities=total_activities,
        activities=total_activities,
        travel=travel_val,
        travel_co2e=travel_val,
        electricity=elec_val,
        electricity_co2e=elec_val,
        food=food_val,
        food_co2e=food_val,
        reduction=reduction,
        reduction_percent=reduction,
        goal=goal_dict,
        goal_progress=goal_dict,
        categories=DashboardCategories(
            travel=category_map["travel"],
            electricity=category_map["electricity"],
            food=category_map["food"],
        ),
    )
