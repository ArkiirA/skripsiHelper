from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject, Section
from skripsi_helper.models.snapshot import Snapshot
from skripsi_helper.models.schema import SnapshotOut, SectionOut
from skripsi_helper.api.v1.auth import get_current_user

router = APIRouter(tags=["snapshots"])


@router.get("/sections/{section_id}/snapshots", response_model=List[SnapshotOut])
def list_section_snapshots(
    section_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List snapshots for a section with timestamps."""
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

    snapshots = db.execute(
        select(Snapshot)
        .where(Snapshot.section_id == section_id)
        .order_by(Snapshot.created_at.desc())
    ).scalars().all()

    return snapshots


@router.get("/snapshots/{snapshot_id}", response_model=SnapshotOut)
def get_snapshot(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Preview a snapshot's content."""
    snapshot = db.execute(
        select(Snapshot)
        .join(SkripsiProject)
        .where(Snapshot.id == snapshot_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snapshot not found",
        )

    return snapshot


@router.post("/snapshots/{snapshot_id}/restore", response_model=SectionOut)
def restore_snapshot(
    snapshot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Restore a snapshot to its section, creating a pre-restore backup snapshot first."""
    snapshot = db.execute(
        select(Snapshot)
        .join(SkripsiProject)
        .where(Snapshot.id == snapshot_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not snapshot or getattr(snapshot, "section_id", None) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snapshot or linked section not found",
        )

    section = db.execute(
        select(Section).where(Section.id == snapshot.section_id)
    ).scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found",
        )

    # Backup current state before restoring if different
    if getattr(section, "content", None) != getattr(snapshot, "content_snapshot", None):
        backup = Snapshot(
            skripsi_project_id=section.skripsi_project_id,
            section_id=section.id,
            content_snapshot=section.content,
            word_count=section.word_count,
            note=f"Pre-restore backup (before reverting to snapshot #{snapshot.id})",
            created_at=datetime.utcnow(),
        )
        db.add(backup)

    # Overwrite section with snapshot content
    section.content = snapshot.content_snapshot
    section.word_count = snapshot.word_count
    section.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(section)
    return section
