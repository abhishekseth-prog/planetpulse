"""Activity domain service for business logic and database persistence."""

import datetime as dt
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate
from app.carbon.calculator import calculate_co2e


def create_activity(
    db: Session,
    activity_in: ActivityCreate,
    user_id: Optional[int] = None,
) -> Activity:
    """Calculate emissions using the centralized Carbon Engine and persist activity.

    Args:
        db: SQLAlchemy database session.
        activity_in: Validated activity input schema.
        user_id: Optional authenticated user ID.

    Returns:
        Activity: Persisted database record including calculated co2e.
    """
    # 1. Pure calculation via centralized Carbon Engine (zero duplicate formulas)
    co2e_val = calculate_co2e(
        activity=activity_in.activity,
        amount=activity_in.amount,
        unit=activity_in.unit,
    )

    # 2. Database model instantiation and persistence
    db_activity = Activity(
        user_id=user_id,
        category=activity_in.category,
        activity=activity_in.activity,
        amount=activity_in.amount,
        unit=activity_in.unit,
        date=activity_in.date,
        co2e=co2e_val,
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_activities(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    category: Optional[str] = None,
) -> List[Activity]:
    """Retrieve activities with optional user scoping, date filtering, and category filtering."""
    query = db.query(Activity)

    if user_id is not None:
        query = query.filter(Activity.user_id == user_id)

    if start_date is not None:
        query = query.filter(Activity.date >= start_date)

    if end_date is not None:
        query = query.filter(Activity.date <= end_date)

    if category is not None:
        cat_norm = category.strip().lower()
        query = query.filter(Activity.category == cat_norm)

    return query.order_by(Activity.date.desc(), Activity.id.desc()).all()
