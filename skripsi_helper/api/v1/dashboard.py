from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from skripsi_helper.db.session import get_session
from skripsi_helper.models.skripsi import SkripsiProject, Section
from skripsi_helper.models.pedoman import PedomanPreset
from skripsi_helper.models.konsultasi import KonsultasiLog
from skripsi_helper.api.v1.auth import get_current_user
from skripsi_helper.models.user import User

router = APIRouter(prefix="/projects", tags=["dashboard"])


@router.get("/{project_id}/dashboard", response_model=Any)
def get_dashboard(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get progress dashboard for a skripsi project."""
    project = db.execute(
        select(SkripsiProject)
        .where(SkripsiProject.id == project_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Get pedoman preset if assigned
    pedoman_data = None
    pedoman_id = getattr(project, "pedoman_preset_id", None)
    if pedoman_id:
        preset = db.execute(
            select(PedomanPreset).where(PedomanPreset.id == pedoman_id)
        ).scalar_one_or_none()
        if preset:
            pedoman_data = {
                "id": preset.id,
                "name": preset.name,
                "university": preset.university,
                "faculty": preset.faculty,
                "preset_data": preset.preset_data,
            }

    # Get sections with word counts
    sections = db.execute(
        select(Section)
        .where(Section.skripsi_project_id == project_id)
        .order_by(Section.order)
    ).scalars().all()

    total_sections = len(sections)
    completed_sections = 0
    total_words = 0
    for s in sections:
        wc = getattr(s, "word_count", 0) or 0
        total_words += wc
        if bool(getattr(s, "is_completed", False)) or wc > 0:
            completed_sections += 1
    overall_completion = round((completed_sections / total_sections * 100), 1) if total_sections > 0 else 0

    # Unresolved konsultasi count
    unresolved_count = db.execute(
        select(func.count(KonsultasiLog.id))
        .where(KonsultasiLog.skripsi_project_id == project_id)
        .where(KonsultasiLog.is_resolved.is_(False))
    ).scalar() or 0

    return {
        "project_id": project.id,
        "project_title": project.title,
        "pedoman": pedoman_data,
        "sections": [
            {
                "id": s.id,
                "title": s.title,
                "slug": s.slug,
                "order": s.order,
                "word_count": s.word_count or 0,
                "is_completed": bool(s.is_completed),
                "has_content": (s.word_count or 0) > 0,
                "status": s.status,
            }
            for s in sections
        ],
        "progress": {
            "total_sections": total_sections,
            "completed_sections": completed_sections,
            "overall_completion": overall_completion,
            "total_words": total_words,
        },
        "konsultasi": {
            "unresolved_count": unresolved_count,
        },
        "generated_at": datetime.utcnow().isoformat(),
    }
