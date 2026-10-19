from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject, Section
from skripsi_helper.models.schema import SectionOut, SectionUpdate
from skripsi_helper.api.v1.auth import get_current_user

router = APIRouter(prefix="/sections", tags=["sections"])


@router.get("/{section_id}", response_model=SectionOut)
def get_section(
    section_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get section details by ID."""
    section = db.execute(
        select(Section)
        .join(SkripsiProject)
        .where(Section.id == section_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )

    return section


@router.patch("/{section_id}", response_model=SectionOut)
def update_section(
    section_id: int,
    section_in: SectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Auto-save section content, word count, or status."""
    section = db.execute(
        select(Section)
        .join(SkripsiProject)
        .where(Section.id == section_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )

    if section_in.content is not None:
        section.content = section_in.content
    if section_in.word_count is not None:
        section.word_count = section_in.word_count
    if section_in.is_completed is not None:
        section.is_completed = section_in.is_completed
    if section_in.status is not None:
        section.status = section_in.status

    section.updated_at = datetime.utcnow()

    # Update project last_saved and aggregate word_count
    project = db.execute(
        select(SkripsiProject).where(SkripsiProject.id == section.skripsi_project_id)
    ).scalar_one_or_none()

    if project:
        project.last_saved = datetime.utcnow()
        total_words = db.execute(
            select(func.coalesce(func.sum(Section.word_count), 0)).where(
                Section.skripsi_project_id == project.id
            )
        ).scalar() or 0
        project.word_count = total_words

    db.commit()
    db.refresh(section)
    return section
