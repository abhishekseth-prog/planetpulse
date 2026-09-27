"""API route for dashboard statistics and emission aggregations."""

import datetime as dt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard_summary
from app.services.auth_dependencies import get_optional_current_user

router = APIRouter(tags=["dashboard"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Retrieve carbon emission dashboard summaries and category breakdown",
)
def get_dashboard(
    start_date: Optional[dt.date] = Query(None, description="Filter activities starting on or after this date (YYYY-MM-DD)"),
    end_date: Optional[dt.date] = Query(None, description="Filter activities ending on or before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve overall emissions total, total activity count, and categorical breakdown.

    Optionally filter by start_date and/or end_date.
    Returns HTTP 422 if start_date > end_date.
    """
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"start_date ({start_date}) cannot be greater than end_date ({end_date})",
        )

    user_id = current_user.id if current_user else None
    return get_dashboard_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
    )
