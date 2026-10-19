from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class Payment(Base):
    """Payment — Midtrans transaction tracking."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=True)

    transaction_id = Column(String, unique=True, nullable=False)  # Midtrans ID
    payment_type = Column(String, nullable=False)  # qris, gopay, ovo, bank_transfer
    amount = Column(Integer, default=50000)  # Rp 50,000
    currency = Column(String, default="IDR")
    payment_status = Column(String, default="pending")  # pending, settlement, cancel, deny, expire
    is_premium_unlocked = Column(Boolean, default=False)

    # Midtrans metadata
    snap_token = Column(String, nullable=True)
    redirection_url = Column(String, nullable=True)
    transaction_time = Column(DateTime, nullable=True)
    settlement_time = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payments")
    skripsi_project = relationship("SkripsiProject", back_populates="payments")
