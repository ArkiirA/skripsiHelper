from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from skripsi_helper.db.session import Base


class PedomanPreset(Base):
    """Pedoman preset — university formatting rules."""
    __tablename__ = "pedoman_presets"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "UI - Fakultas Hukum 2024"
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    flags = Column(Integer, default=0)

    # Formatting rules (stored as JSONB)
    page_size = Column(String, default="A4")  # A4, Letter
    margins = Column(JSON, default={
        "top": 3.0, "bottom": 3.0, "left": 4.0, "right": 3.0
    })  # cm
    font_body = Column(String, default="Times New Roman")
    font_size_body = Column(Integer, default=12)
    font_heading = Column(String, default="Times New Roman")
    font_size_heading = Column(Integer, default=14)
    line_spacing = Column(String, default="1.5")  # 1.0, 1.5, 2.0
    citation_style = Column(String, default="apa")  # apa, ieee, vancouver, chicago, harvard
    heading_format = Column(JSON, default={  # numbering format per level
        "level_1": "%d",
        "level_2": "%d.%d",
        "level_3": "%d.%d.%d",
    })
    page_numbering = Column(JSON, default={
        "front_matter": "roman",  # i, ii, iii
        "body": "arabic",  # 1, 2, 3
        "front_start_page": 1,
    })
    required_sections = Column(JSON, default=[  # BABs and sub-sections
        {"title": "Latar Belakang", "min_pages": 2},
        {"title": "Rumusan Masalah", "min_pages": 1},
        {"title": "Tujuan Penelitian", "min_pages": 1},
        {"title": "Manfaat Penelitian", "min_pages": 1},
        {"title": "Tinjauan Pustaka", "min_pages": 5},
        {"title": "Metodologi Penelitian", "min_pages": 3},
        {"title": "Hasil dan Pembahasan", "min_pages": 5},
        {"title": "Kesimpulan dan Saran", "min_pages": 2},
    ])
    cover_page = Column(JSON, default={
        "title": "TUGAS AKHIR",
        "subtitle": "Skripsi",
        "required_fields": ["title", "author", "university", "date"],
    })

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    university = relationship("University", back_populates="pedoman_presets")
    skripsi_projects = relationship("SkripsiProject", back_populates="pedoman_preset")
