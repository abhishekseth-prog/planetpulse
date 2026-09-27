from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.insights import InsightsResponse
from app.services.insights_service import get_insights
from app.services.auth_dependencies import get_optional_current_user

router = APIRouter(tags=["insights"])


@router.get(
    "/insights",
    response_model=InsightsResponse,
    summary="Retrieve personalized carbon reduction insights",
)
def fetch_insights(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Provide rule-based insights and recommendations based on current month emissions."""
    user_id = current_user.id if current_user else None
    return get_insights(db=db, user_id=user_id)
