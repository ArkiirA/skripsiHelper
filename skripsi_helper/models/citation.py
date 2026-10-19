from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class UploadedPdf(Base):
    """Uploaded PDF file reference — stored in GCS."""
    __tablename__ = "uploaded_pdfs"

    id = Column(Integer, primary_key=True, index=True)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    gcs_path = Column(String, unique=True, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    mime_type = Column(String, default="application/pdf")
    extracted_doi = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    extraction_error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skripsi_project = relationship("SkripsiProject", back_populates="uploaded_pdfs")
    citation = relationship("Citation", back_populates="uploaded_pdf", uselist=False)


class Citation(Base):
    """Citation — reference in the bibliography."""
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    skripsi_project_id = Column(Integer, ForeignKey("skripsi_projects.id"), nullable=False)
    uploaded_pdf_id = Column(Integer, ForeignKey("uploaded_pdfs.id"), nullable=True)

    # Metadata — extracted or manual
    title = Column(String, nullable=False)
    authors = Column(JSON, nullable=False)  # [{"name": "John Doe", "orcid": "..."}]
    year = Column(Integer, nullable=False)
    journal = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    issue = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    doi = Column(String, unique=True, nullable=True)
    url = Column(String, nullable=True)
    citation_string = Column(String, nullable=False)  # formatted per pedoman style
    citation_style = Column(String, default="apa")  # apa, ieee, vancouver, chicago, harvard

    # Source tracking
    is_manual = Column(Boolean, default=False)
    source = Column(String, default="auto")  # auto, manual, doi_lookup, openalex

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skripsi_project = relationship("SkripsiProject", back_populates="citations")
    uploaded_pdf = relationship("UploadedPdf", back_populates="citation")
