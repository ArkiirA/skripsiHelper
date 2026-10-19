from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class Snapshot(Base):
    """Snapshot — version history for sections."""
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)  # null = full project snapshot

    content_snapshot = Column(String, nullable=False)  # Tiptap JSON or plain text
    note = Column(String, nullable=True)  # user-provided snapshot label

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skripsi_project = relationship("SkripsiProject", back_populates="snapshots")
