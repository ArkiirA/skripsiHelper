from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class KonsultasiLog(Base):
    """Konsultasi log — advisor feedback tracking."""
    __tablename__ = "konsultasi_logs"

    id = Column(Integer, primary_key=True, index=True)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=False)

    date = Column(DateTime, nullable=False)  # bimbingan session date
    notes = Column(Text, nullable=False)
    action_items = Column(JSON, default=[])  # [{"task": "...", "due": "...", "done": false}]
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skripsi_project = relationship("SkripsiProject", back_populates="konsultasi_entries")
