"""Trend aggregation service.

Aggregates stored Activity.co2e directly from the database.
"""

import datetime as dt
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.schemas.trend import TrendPoint, TrendResponse


def get_trend_data(
    db: Session,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    user_id: Optional[int] = None,
) -> TrendResponse:
    """Aggregate daily emissions and activity counts ordered chronologically.

    Args:
        db: Active SQLAlchemy database session.
        start_date: Optional start date filter (inclusive).
        end_date: Optional end date filter (inclusive).
        user_id: Optional user ID for account scoping.

    Returns:
        TrendResponse: List of daily TrendPoints sorted in ascending order.
    """
    filters = []
    if user_id is not None:
        filters.append(Activity.user_id == user_id)
    if start_date is not None:
        filters.append(Activity.date >= start_date)
    if end_date is not None:
        filters.append(Activity.date <= end_date)

    query = db.query(
        Activity.date.label("date"),
        func.coalesce(func.sum(Activity.co2e), 0.0).label("co2e"),
        func.count(Activity.id).label("activities"),
    )
    if filters:
        query = query.filter(*filters)

    results = query.group_by(Activity.date).order_by(Activity.date.asc()).all()

    points = [
        TrendPoint(
            date=row.date,
            co2e=round(float(row.co2e), 4),
            activities=int(row.activities),
        )
        for row in results
    ]

    return TrendResponse(trend=points)


def get_period_trend_data(
    db: Session,
    period: str,
    user_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return zero-filled date points for period (7d, 30d, 3m)."""
    days_map = {"7d": 7, "30d": 30, "3m": 90}
    days = days_map.get(period, 7)
    today = dt.date.today()
    start_day = today - dt.timedelta(days=days - 1)

    query = db.query(
        Activity.date.label("date"),
        func.coalesce(func.sum(Activity.co2e), 0.0).label("co2e"),
    ).filter(Activity.date >= start_day, Activity.date <= today)

    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)

    results = query.group_by(Activity.date).order_by(Activity.date.asc()).all()
    by_date = {row.date.isoformat(): round(float(row.co2e), 3) for row in results}

    output = []
    for offset in range(days):
        current_day = start_day + dt.timedelta(days=offset)
        iso = current_day.isoformat()
        label = current_day.strftime("%a" if days == 7 else "%d %b")
        output.append({
            "date": iso,
            "label": label,
            "co2e": by_date.get(iso, 0.0),
        })
    return output
