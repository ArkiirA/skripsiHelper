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
    content: Optional[Any] = None
    word_count: int = 0
    status: str = "active"
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
    is_premium: bool = False
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
    content: Optional[Any] = None
    is_completed: Optional[bool] = None
    word_count: Optional[int] = None
    status: Optional[str] = None


class SnapshotOut(BaseModel):
    """Snapshot response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    skripsi_project_id: int
    section_id: Optional[int] = None
    word_count: int = 0
    note: Optional[str] = None
    created_at: datetime
    content_snapshot: Optional[Any] = None


class CitationCreateManual(BaseModel):
    """Manual citation entry request."""
    title: str
    authors: List[Any]
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_style: Optional[str] = "apa"
    section_id: Optional[int] = None


class DoiLookupRequest(BaseModel):
    """Lookup citation via DOI string."""
    doi: str
    section_id: Optional[int] = None


class CitationOut(BaseModel):
    """Citation response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    skripsi_project_id: int
    section_id: Optional[int] = None
    uploaded_pdf_id: Optional[int] = None
    title: str
    authors: List[Any]
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_string: Optional[str] = None
    citation_style: str = "apa"
    is_manual: bool = False
    needs_manual_completion: bool = False
    source: str = "auto"
    created_at: datetime


class KonsultasiCreate(BaseModel):
    """Request to create a konsultasi log entry."""
    notes: str
    date: Optional[datetime] = None
    action_items: Optional[List[Any]] = None


class KonsultasiOut(BaseModel):
    """Konsultasi log response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    skripsi_project_id: int
    date: datetime
    notes: str
    action_items: List[Any] = []
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: datetime


class KonsultasiSummaryOut(BaseModel):
    """Summary of konsultasi log for reminders & dashboard."""
    total_entries: int
    unresolved_count: int
    resolved_count: int
    unresolved_entries: List[KonsultasiOut]


# AI Assist schemas
class OutlineRequest(BaseModel):
    """Request for outline suggestion."""
    project_id: int
    topic: str
    pedoman_sections: Optional[List[str]] = None


class OutlineResponse(BaseModel):
    """Response with suggested outline."""
    outline: str


class ParaphraseRequest(BaseModel):
    """Request for paraphrasing."""
    text: str
    tone: Optional[str] = "academic"


class ParaphraseResponse(BaseModel):
    """Response with paraphrased text."""
    paraphrase: str


class CheckRequest(BaseModel):
    """Request for grammar/style checking."""
    text: str
    project_id: Optional[int] = None
    language: Optional[str] = "id-ID"
    pedoman_sections: Optional[List[str]] = None


class CheckResponse(BaseModel):
    """Response with check results."""
    matches: Optional[List[Any]] = None
    language: Optional[str] = None
    analysis: Optional[str] = None


# Payment schemas
class PaymentInitiateRequest(BaseModel):
    """Request to initiate Midtrans payment for project premium unlock."""
    skripsi_project_id: int
    payment_type: Optional[str] = "qris"


class PaymentInitiateResponse(BaseModel):
    """Response from initiating Midtrans Snap transaction."""
    payment_id: int
    order_id: str
    snap_token: Optional[str] = None
    redirection_url: Optional[str] = None
    amount: int = 50000
    already_premium: bool = False


class PaymentStatusResponse(BaseModel):
    """Payment transaction status response."""
    payment_id: int
    order_id: str
    payment_status: str
    is_premium_unlocked: bool
    payment_type: Optional[str] = None
    amount: int = 50000


class ProjectPaymentStatusOut(BaseModel):
    """Payment status for project settings."""
    project_id: int
    is_premium: bool
    status: str  # "free" or "premium"
    payment_status: Optional[str] = None
    amount: int = 50000

