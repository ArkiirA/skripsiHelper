from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class SkripsiProject(Base):
    """Skripsi project — user's thesis project."""
    __tablename__ = "skripsi_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pedoman_preset_id = Column(Integer, ForeignKey("pedoman_presets.id"), nullable=True)

    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    status = Column(String, default="draft")  # draft, writing, review, submitted

    # Progress tracking
    word_count = Column(Integer, default=0)
    completion_percentage = Column(Integer, default=0)
    last_saved = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="skripsi_projects")
    pedoman_preset = relationship("PedomanPreset", back_populates="skripsi_projects")
    sections = relationship("Section", back_populates="skripsi_project", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="skripsi_project", cascade="all, delete-orphan")
    uploaded_pdfs = relationship("UploadedPdf", back_populates="skripsi_project", cascade="all, delete-orphan")
    konsultasi_entries = relationship("KonsultasiLog", back_populates="skripsi_project", cascade="all, delete-orphan")
    snapshots = relationship("Snapshot", back_populates="skripsi_project", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="skripsi_project")


class Section(Base):
    """Section — single chapter/section content."""
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    content = Column(Text, default="")  # Tiptap JSON or plain text
    order = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    word_count = Column(Integer, default=0)
    status = Column(String, default="active")  # active, archived, placeholder

    # Optional pedoman constraints (override preset defaults)
    min_pages = Column(Integer, nullable=True)
    max_pages = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skripsi_project = relationship("SkripsiProject", back_populates="sections")
    citations = relationship("Citation", back_populates="section", cascade="all, delete-orphan")
    uploaded_pdfs = relationship("UploadedPdf", back_populates="section", cascade="all, delete-orphan")
