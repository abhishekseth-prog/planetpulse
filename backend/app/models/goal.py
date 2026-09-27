from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from app.database import Base


class UserGoal(Base):
    """SQLAlchemy model representing a user's monthly carbon goal target."""
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    goal_month = Column(String(7), nullable=False, index=True)  # Format: YYYY-MM
    target_kg = Column(Float, nullable=False, default=100.0)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "goal_month", name="uq_user_goal_month"),
    )

    def __repr__(self) -> str:
        return f"<UserGoal(user_id={self.user_id}, goal_month='{self.goal_month}', target_kg={self.target_kg})>"
