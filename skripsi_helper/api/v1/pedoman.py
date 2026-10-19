from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from skripsi_helper.core.config import settings
from skripsi_helper.db.session import get_session
from skripsi_helper.models.pedoman import PedomanPreset, University
from skripsi_helper.api.v1.auth import get_current_active_user, GoogleUser

router = APIRouter(prefix="/pedoman", tags=["pedoman"])


class PedomanPresetCreate(BaseModel):
    university_name: str
    page_margin_top: float = 2.5
    page_margin_bottom: float = 2.5
    page_margin_left: float = 3.0
    page_margin_right: float = 2.5
    paper_size: str = "A4"
    font_family_body: str = "Times New Roman"
    font_size_body: int = 12
    font_family_heading: str = "Arial"
    font_size_heading: int = 14
    line_spacing: float = 1.5
    citation_style: str = "APA"
    heading_numbering_format: str = "1.1.1"
    page_numbering_rules: str = "bottom-center"
    sections: List[dict]
    min_pages_per_section: int | None = None
    max_pages_per_section: int | None = None


class PedomanPresetRead(BaseModel):
    id: int
    university_name: str
    page_margin_top: float
    page_margin_bottom: float
    page_margin_left: float
    page_margin_right: float
    paper_size: str
    font_family_body: str
    font_size_body: int
    font_family_heading: str
    font_size_heading: int
    line_spacing: float
    citation_style: str
    heading_numbering_format: str
    page_numbering_rules: str
    sections: List[dict]
    min_pages_per_section: int | None
    max_pages_per_section: int | None
    usage_count: int
    created_at: str


@router.post("/", response_model=PedomanPresetRead)
def create_pedoman_preset(
    preset: PedomanPresetCreate,
    db: Session = Depends(get_session),
    current_user: GoogleUser = Depends(get_current_active_user),
):
    """Create a new pedoman preset."""
    db_preset = PedomanPreset(
        university_name=preset.university_name,
        page_margin_top=preset.page_margin_top,
        page_margin_bottom=preset.page_margin_bottom,
        page_margin_left=preset.page_margin_left,
        page_margin_right=preset.page_margin_right,
        paper_size=preset.paper_size,
        font_family_body=preset.font_family_body,
        font_size_body=preset.font_size_body,
        font_family_heading=preset.font_family_heading,
        font_size_heading=preset.font_size_heading,
        line_spacing=preset.line_spacing,
        citation_style=preset.citation_style,
        heading_numbering_format=preset.heading_numbering_format,
        page_numbering_rules=preset.page_numbering_rules,
        sections=preset.sections,
        min_pages_per_section=preset.min_pages_per_section,
        max_pages_per_section=preset.max_pages_per_section,
        created_by=current_user.email,
    )
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return db_preset


@router.get("/", response_model=List[PedomanPresetRead])
def list_pedoman_presets(
    university_name: str | None = None,
    db: Session = Depends(get_session),
):
    """List pedoman presets, optionally filtered by university name."""
    statement = select(PedomanPreset).order_by(PedomanPreset.usage_count.desc())
    if university_name:
        statement = statement.where(
            PedomanPreset.university_name.ilike(f"%{university_name}%")
        )
    presets = db.execute(statement).scalars().all()
    return presets


@router.get("/{preset_id}", response_model=PedomanPresetRead)
def get_pedoman_preset(preset_id: int, db: Session = Depends(get_session)):
    """Get a specific pedoman preset by ID."""
    preset = db.get(PedomanPreset, preset_id)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedoman preset not found",
        )
    return preset


@router.post("/{preset_id}/flag")
def flag_pedoman_preset(
    preset_id: int,
    db: Session = Depends(get_session),
    current_user: GoogleUser = Depends(get_current_active_user),
):
    """Flag a pedoman preset as inaccurate."""
    preset = db.get(PedomanPreset, preset_id)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedoman preset not found",
        )
    # TODO: Implement flagging logic (store in separate table)
    return {"message": "Flag submitted for review"}
