from datetime import datetime
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject
from skripsi_helper.models.konsultasi import KonsultasiLog
from skripsi_helper.models.schema import KonsultasiCreate, KonsultasiOut, KonsultasiSummaryOut
from skripsi_helper.api.v1.auth import get_current_user

router = APIRouter(tags=["konsultasi"])


def verify_project_ownership(project_id: int, user_id: Any, db: Session) -> SkripsiProject:
    """Ensure user owns the project."""
    project = db.execute(
        select(SkripsiProject)
        .where(SkripsiProject.id == project_id)
        .where(SkripsiProject.user_id == user_id)
    ).scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.post("/projects/{project_id}/konsultasi", response_model=KonsultasiOut, status_code=status.HTTP_201_CREATED)
def create_konsultasi_log(
    project_id: int,
    log_in: KonsultasiCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create a new bimbingan / konsultasi log entry."""
    verify_project_ownership(project_id, current_user.id, db)

    entry = KonsultasiLog(
        skripsi_project_id=project_id,
        date=log_in.date or datetime.utcnow(),
        notes=log_in.notes,
        action_items=log_in.action_items or [],
        is_resolved=False,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/projects/{project_id}/konsultasi", response_model=List[KonsultasiOut])
def list_konsultasi_logs(
    project_id: int,
    resolved: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List konsultasi logs chronologically."""
    verify_project_ownership(project_id, current_user.id, db)

    statement = select(KonsultasiLog).where(KonsultasiLog.skripsi_project_id == project_id)
    if resolved is not None:
        statement = statement.where(KonsultasiLog.is_resolved == resolved)

    statement = statement.order_by(desc(KonsultasiLog.date))
    return db.execute(statement).scalars().all()


@router.get("/projects/{project_id}/konsultasi/summary", response_model=KonsultasiSummaryOut)
def get_konsultasi_summary(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get count and active reminders of unresolved bimbingan action items."""
    verify_project_ownership(project_id, current_user.id, db)

    all_logs = db.execute(
        select(KonsultasiLog)
        .where(KonsultasiLog.skripsi_project_id == project_id)
        .order_by(desc(KonsultasiLog.date))
    ).scalars().all()

    unresolved = [
        KonsultasiOut.model_validate(l)
        for l in all_logs
        if not getattr(l, "is_resolved", False)
    ]
    resolved = [
        KonsultasiOut.model_validate(l)
        for l in all_logs
        if getattr(l, "is_resolved", False)
    ]

    return KonsultasiSummaryOut(
        total_entries=len(all_logs),
        unresolved_count=len(unresolved),
        resolved_count=len(resolved),
        unresolved_entries=unresolved,
    )


@router.patch("/konsultasi/{log_id}/toggle-resolved", response_model=KonsultasiOut)
def toggle_konsultasi_resolved(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Toggle resolved/unresolved status on an entry."""
    entry = db.execute(
        select(KonsultasiLog)
        .join(SkripsiProject)
        .where(KonsultasiLog.id == log_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Konsultasi log entry not found",
        )

    # Toggle
    current_status = getattr(entry, "is_resolved", False)
    new_status = not bool(current_status)
    setattr(entry, "is_resolved", new_status)
    setattr(entry, "resolved_at", datetime.utcnow() if new_status else None)
    setattr(entry, "updated_at", datetime.utcnow())

    db.commit()
    db.refresh(entry)
    return entry
