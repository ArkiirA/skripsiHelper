from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class Snapshot(Base):
    """Snapshot — version history for sections."""
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    content_snapshot = Column(JSON, nullable=False)  # Tiptap JSON AST or dict
    word_count = Column(Integer, default=0)
    note = Column(String, nullable=True)  # user-provided label or auto-save

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skripsi_project = relationship("SkripsiProject", back_populates="snapshots")
    section = relationship("Section", back_populates="snapshots")
