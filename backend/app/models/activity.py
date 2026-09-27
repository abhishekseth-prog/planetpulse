from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from app.database import Base


class Activity(Base):
    """SQLAlchemy model representing an individual recorded activity.

    Fields:
      - id: Unique integer identifier (primary key)
      - user_id: Optional Foreign key referencing users.id for multi-user isolation
      - category: Broad classification ('travel', 'electricity', 'food')
      - activity: Specific activity type ('car', 'ac', 'chicken_meal', etc.)
      - amount: Numeric measurement value (must be > 0)
      - unit: Measurement unit ('km', 'hours', 'meal', etc.)
      - date: Date when the activity occurred
      - co2e: Carbon emissions in kg CO2e calculated by the Carbon Engine
      - created_at: Timestamp when record was saved
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    activity = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    date = Column(Date, nullable=False, index=True)
    co2e = Column(Float, nullable=False, default=0.0)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Activity(id={self.id}, user_id={self.user_id}, category='{self.category}', "
            f"activity='{self.activity}', amount={self.amount}, "
            f"unit='{self.unit}', date='{self.date}', co2e={self.co2e})>"
        )
