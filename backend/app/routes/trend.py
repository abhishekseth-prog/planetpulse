"""API route for carbon emission trend data."""

import datetime as dt
from typing import Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.trend import TrendResponse
from app.services.trend_service import get_trend_data, get_period_trend_data
from app.services.auth_dependencies import get_optional_current_user

router = APIRouter(tags=["trend"])


@router.get(
    "/trend",
    summary="Retrieve carbon emission trend data",
)
def get_trend(
    period: Optional[str] = Query(None, description="Preset period: 7d, 30d, 3m"),
    start_date: Optional[dt.date] = Query(None, description="Filter activities starting on or after this date (YYYY-MM-DD)"),
    end_date: Optional[dt.date] = Query(None, description="Filter activities ending on or before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Any:
    """Retrieve chronologically sorted daily carbon emission trends.

    If 'period' is specified (7d, 30d, 3m), returns zero-filled daily points.
    Otherwise, returns TrendResponse with active days.
    """
    if period is not None:
        if period not in ("7d", "30d", "3m"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid period '{period}'. Allowed: 7d, 30d, 3m",
            )
        user_id = current_user.id if current_user else None
        return get_period_trend_data(db=db, period=period, user_id=user_id)

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"start_date ({start_date}) cannot be greater than end_date ({end_date})",
        )

    user_id = current_user.id if current_user else None
    return get_trend_data(
        db=db,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
    )
