from typing import List, Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SectionTemplate(BaseModel):
    """Template for a section defined in a pedoman preset."""
    title: str
    slug: str
    order: int
    min_pages: Optional[int] = None
    max_pages: Optional[int] = None
    description: Optional[str] = None


class PedomanPresetCreate(BaseModel):
    """Request to create a new pedoman preset."""
    university_id: int
    name: str
    description: Optional[str] = None
    sections: List[SectionTemplate]
    default_margins: Optional[Dict[str, float]] = None
    default_font: Optional[str] = "Times New Roman"
    default_font_size: Optional[int] = 12
    default_line_spacing: Optional[float] = 1.5
    citation_style: Optional[str] = "APA"


class PedomanPresetUpdate(BaseModel):
    """Request to update a pedoman preset."""
    name: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[List[SectionTemplate]] = None
    default_margins: Optional[Dict[str, float]] = None
    default_font: Optional[str] = None
    default_font_size: Optional[int] = None
    default_line_spacing: Optional[float] = None
    citation_style: Optional[str] = None


class SectionOut(BaseModel):
    """Section response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    order: int
    min_pages: Optional[int] = None
    max_pages: Optional[int] = None
    description: Optional[str] = None


class PedomanPresetOut(BaseModel):
    """Pedoman preset response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    university_id: int
    name: str
    description: Optional[str] = None
    sections: List[SectionOut]
    default_margins: Optional[Dict[str, float]] = None
    default_font: str = "Times New Roman"
    default_font_size: int = 12
    default_line_spacing: float = 1.5
    citation_style: str = "APA"
    is_default: bool = False
    usage_count: int = 0


class SkripsiProjectCreate(BaseModel):
    """Request to create a new skripsi project."""
    title: str
    topic: str
    pedoman_preset_id: int


class SkripsiProjectOut(BaseModel):
    """Skripsi project response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    topic: str
    pedoman_preset_id: Optional[int] = None
    is_active: bool = True
    status: str = "draft"
    word_count: int = 0
    completion_percentage: int = 0
    last_saved: datetime
    created_at: datetime
    updated_at: datetime


class SectionCreate(BaseModel):
    """Request to create a section."""
    title: str
    slug: str
    order: int
    content: str = ""


class SectionUpdate(BaseModel):
    """Request to update a section."""
    content: Optional[str] = None
    is_completed: Optional[bool] = None
    word_count: Optional[int] = None
    status: Optional[str] = None
