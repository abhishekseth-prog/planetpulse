"""API route for activity ingestion and retrieval."""

import datetime as dt
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services.activity_service import create_activity, get_activities
from app.services.auth_dependencies import get_optional_current_user
from app.carbon.exceptions import CarbonEngineError

router = APIRouter(tags=["activities"])


@router.post(
    "/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record daily activity and compute personal emissions",
)
def record_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Receive activity data, calculate CO2e emissions, persist record, and return response."""
    try:
        user_id = current_user.id if current_user else None
        return create_activity(db=db, activity_in=activity_in, user_id=user_id)
    except CarbonEngineError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/activities",
    response_model=List[ActivityResponse],
    summary="Retrieve activity history",
)
def list_activities(
    category: Optional[str] = Query(None, description="Filter by category (travel, electricity, food)"),
    start_date: Optional[dt.date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[dt.date] = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve logged activities with optional date, category, and authenticated user filtering."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date cannot be greater than end_date",
        )
    user_id = current_user.id if current_user else None
    return get_activities(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=category,
    )
