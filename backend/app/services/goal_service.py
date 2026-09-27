"""Goal progress calculation and aggregation service.

Aggregates stored Activity.co2e directly from the database.
"""

import calendar
import datetime as dt
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import DEFAULT_MONTHLY_GOAL_CO2E
from app.models.activity import Activity
from app.models.goal import UserGoal
from app.schemas.goal import GoalResponse, MonthlyGoalProgressResponse


def get_user_month_target(db: Session, user_id: Optional[int], month_str: str) -> float:
    """Retrieve stored goal target for a user and month, or default."""
    query = db.query(UserGoal).filter(UserGoal.goal_month == month_str)
    if user_id is not None:
        query = query.filter(UserGoal.user_id == user_id)
    else:
        query = query.filter(UserGoal.user_id.is_(None))

    user_goal = query.first()
    if user_goal:
        return float(user_goal.target_kg)
    return DEFAULT_MONTHLY_GOAL_CO2E


def set_user_month_target(db: Session, user_id: Optional[int], month_str: str, target: float) -> float:
    """Set or update stored goal target for a user (or anonymous default) and month."""
    query = db.query(UserGoal).filter(UserGoal.goal_month == month_str)
    if user_id is not None:
        query = query.filter(UserGoal.user_id == user_id)
    else:
        query = query.filter(UserGoal.user_id.is_(None))

    user_goal = query.first()
    if user_goal:
        user_goal.target_kg = target
    else:
        user_goal = UserGoal(user_id=user_id, goal_month=month_str, target_kg=target)
        db.add(user_goal)
    db.commit()
    db.refresh(user_goal)
    return float(user_goal.target_kg)


def get_goal_progress(
    db: Session,
    month: Optional[int] = None,
    year: Optional[int] = None,
    target_goal: Optional[float] = None,
    user_id: Optional[int] = None,
) -> GoalResponse:
    """Calculate progress against the monthly carbon goal for a given month and year (legacy contract)."""
    today = dt.date.today()
    target_month = month if month is not None else today.month
    target_year = year if year is not None else today.year
    month_str = f"{target_year:04d}-{target_month:02d}"

    goal = (
        float(target_goal)
        if target_goal is not None
        else get_user_month_target(db, user_id, month_str)
    )

    first_day = dt.date(target_year, target_month, 1)
    _, last_day_num = calendar.monthrange(target_year, target_month)
    last_day = dt.date(target_year, target_month, last_day_num)

    query = db.query(func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= first_day, Activity.date <= last_day
    )
    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)

    current_co2e = round(float(query.scalar()), 4)

    if goal > 0:
        raw_progress = (current_co2e / goal) * 100.0
        progress_percent = round(min(raw_progress, 100.0), 4)
    else:
        progress_percent = 0.0

    if current_co2e < goal:
        remaining_co2e = round(goal - current_co2e, 4)
        over_goal_co2e = 0.0
    else:
        remaining_co2e = 0.0
        over_goal_co2e = round(current_co2e - goal, 4)

    return GoalResponse(
        month=target_month,
        year=target_year,
        goal_co2e=round(goal, 4),
        current_co2e=current_co2e,
        remaining_co2e=remaining_co2e,
        over_goal_co2e=over_goal_co2e,
        progress_percent=progress_percent,
    )


def get_monthly_goal_progress(
    db: Session,
    user_id: Optional[int] = None,
    month_str: Optional[str] = None,
) -> MonthlyGoalProgressResponse:
    """Calculate progress for GET /api/goals/monthly."""
    today = dt.date.today()
    target_month_str = month_str or today.strftime("%Y-%m")
    try:
        yr, mo = map(int, target_month_str.split("-"))
    except Exception:
        yr, mo = today.year, today.month
        target_month_str = today.strftime("%Y-%m")

    target = get_user_month_target(db, user_id, target_month_str)

    first_day = dt.date(yr, mo, 1)
    _, last_day_num = calendar.monthrange(yr, mo)
    last_day = dt.date(yr, mo, last_day_num)

    query = db.query(func.coalesce(func.sum(Activity.co2e), 0.0)).filter(
        Activity.date >= first_day, Activity.date <= last_day
    )
    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)

    current = round(float(query.scalar()), 3)
    prog = round((current / target * 100), 1) if target > 0 else 0.0
    rem = round(max(target - current, 0.0), 3)

    return MonthlyGoalProgressResponse(
        target=target,
        current=current,
        progress=prog,
        remaining=rem,
        target_co2e=target,
        used_co2e=current,
        progress_percent=prog,
        remaining_co2e=rem,
        month=target_month_str,
    )
