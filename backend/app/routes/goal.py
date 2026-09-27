"""API route for carbon goal progress tracking."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.goal import GoalResponse, MonthlyGoalUpdateRequest, MonthlyGoalProgressResponse
from app.services.goal_service import (
    get_goal_progress,
    get_monthly_goal_progress,
    set_user_month_target,
)
from app.services.auth_dependencies import get_optional_current_user

router = APIRouter(tags=["goal"])


@router.get(
    "/goal",
    response_model=GoalResponse,
    summary="Retrieve monthly carbon goal and current progress",
)
def get_goal(
    month: Optional[int] = Query(None, description="Calendar month (1-12)"),
    year: Optional[int] = Query(None, description="Calendar year (e.g. 2026)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Calculate and return monthly carbon budget, actual emissions, and progress.

    Defaults to the current month and year if omitted.
    Returns HTTP 422 for invalid month (< 1 or > 12) or invalid year (< 1900 or > 2100).
    """
    if month is not None:
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Month must be between 1 and 12, received: {month}",
            )

    if year is not None:
        if year < 1900 or year > 2100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Year must be a reasonable four-digit calendar year (1900-2100), received: {year}",
            )

    user_id = current_user.id if current_user else None
    return get_goal_progress(
        db=db,
        month=month,
        year=year,
        user_id=user_id,
    )


@router.get(
    "/goals/monthly",
    response_model=MonthlyGoalProgressResponse,
    summary="Retrieve monthly goal progress",
)
def get_monthly_goals(
    month: Optional[str] = Query(None, description="Target month in YYYY-MM format"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve monthly goal and progress for the authenticated user or default."""
    user_id = current_user.id if current_user else None
    return get_monthly_goal_progress(db=db, user_id=user_id, month_str=month)


@router.put(
    "/goals/monthly",
    response_model=MonthlyGoalProgressResponse,
    summary="Update monthly goal target",
)
def update_monthly_goals(
    payload: MonthlyGoalUpdateRequest,
    month: Optional[str] = Query(None, description="Target month in YYYY-MM format"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Set custom monthly carbon reduction target."""
    import datetime as dt
    user_id = current_user.id if current_user else None
    month_str = month or dt.date.today().strftime("%Y-%m")
    set_user_month_target(db=db, user_id=user_id, month_str=month_str, target=payload.target)
    return get_monthly_goal_progress(db=db, user_id=user_id, month_str=month_str)
