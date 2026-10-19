from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.pedoman import PedomanPreset
from skripsi_helper.models.skripsi import SkripsiProject, Section
from skripsi_helper.models.schema import (
    SkripsiProjectCreate,
    SkripsiProjectOut,
    SectionOut,
    SectionCreate,
    SectionUpdate,
)
from skripsi_helper.api.v1.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=SkripsiProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: SkripsiProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create a new skripsi project and auto-populate sections from the pedoman preset."""
    # Verify preset exists
    preset = db.execute(
        select(PedomanPreset).where(PedomanPreset.id == project_in.pedoman_preset_id)
    ).scalar_one_or_none()
    
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedoman preset with id {project_in.pedoman_preset_id} not found",
        )

    # Create project
    project = SkripsiProject(
        user_id=current_user.id,
        pedoman_preset_id=project_in.pedoman_preset_id,
        title=project_in.title,
        topic=project_in.topic,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Auto-populate sections from preset template
    preset_sections = preset.sections or []
    for s_idx, sec_data in enumerate(preset_sections):
        section = Section(
            skripsi_project_id=project.id,
            title=sec_data.get("title", f"Section {s_idx + 1}"),
            slug=sec_data.get("slug", f"section-{s_idx + 1}"),
            order=sec_data.get("order", s_idx),
            min_pages=sec_data.get("min_pages"),
            max_pages=sec_data.get("max_pages"),
        )
        db.add(section)

    db.commit()
    db.refresh(project)

    return project


@router.get("/", response_model=List[SkripsiProjectOut])
def list_projects(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List skripsi projects for current user."""
    statement = select(SkripsiProject).where(SkripsiProject.user_id == current_user.id)
    if active_only:
        statement = statement.where(SkripsiProject.is_active == True)
    
    return db.execute(statement).scalars().all()


@router.get("/{project_id}", response_model=SkripsiProjectOut)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get project by ID."""
    project = db.execute(
        select(SkripsiProject)
        .where(SkripsiProject.id == project_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch("/{project_id}/archive")
def archive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Archive a project."""
    project = db.execute(
        select(SkripsiProject)
        .where(SkripsiProject.id == project_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project.is_active = False
    db.commit()
    return {"status": "archived"}


@router.patch("/{project_id}/unarchive")
def unarchive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Unarchive a project."""
    project = db.execute(
        select(SkripsiProject)
        .where(SkripsiProject.id == project_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    project.is_active = True
    db.commit()
    return {"status": "unarchived"}


@router.get("/{project_id}/sections", response_model=List[SectionOut])
def get_project_sections(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get sections for a project in outline order."""
    project = db.execute(
        select(SkripsiProject)
        .where(SkripsiProject.id == project_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return db.execute(
        select(Section)
        .where(Section.skripsi_project_id == project_id)
        .order_by(Section.order.asc())
    ).scalars().all()
