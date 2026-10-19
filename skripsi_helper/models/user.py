from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class User(Base):
    """User model — Google OAuth only."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_sub = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    given_name = Column(String, nullable=True)
    family_name = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    ai_actions_today = Column(Integer, default=0)
    last_ai_reset = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skripsi_projects = relationship("SkripsiProject", back_populates="user")
    payments = relationship("Payment", back_populates="user")

    def reset_daily_ai_count(self):
        """Reset AI action count if new day."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if self.last_ai_reset.date() != now.date():
            self.ai_actions_today = 0
            self.last_ai_reset = now
