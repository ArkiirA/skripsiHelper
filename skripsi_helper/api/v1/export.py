from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject, Section
from skripsi_helper.models.citation import Citation
from skripsi_helper.models.pedoman import PedomanPreset
from skripsi_helper.api.v1.auth import get_current_user
from skripsi_helper.services.export import build_docx_document, convert_docx_to_pdf

router = APIRouter(prefix="/projects/{project_id}/export", tags=["export"])


def _get_project_data(project_id: int, user_id: Any, db: Session):
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

    sections = db.execute(
        select(Section)
        .where(Section.skripsi_project_id == project_id)
        .order_by(Section.order)
    ).scalars().all()

    citations = db.execute(
        select(Citation)
        .where(Citation.skripsi_project_id == project_id)
        .order_by(Citation.id)
    ).scalars().all()

    pedoman = None
    if project.pedoman_preset_id is not None:
        pedoman = db.execute(
            select(PedomanPreset)
            .where(PedomanPreset.id == project.pedoman_preset_id)
        ).scalar_one_or_none()

    return project, list(sections), list(citations), pedoman


@router.get("/docx")
def export_docx(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Export project content as formatted DOCX."""
    project, sections, citations, pedoman = _get_project_data(project_id, current_user.id, db)

    try:
        docx_bytes = build_docx_document(
            project=project,
            sections=sections,
            citations=citations,
            pedoman=pedoman,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX: {str(e)}",
        )

    filename = f"{project.title.replace(' ', '_')[:30]}_skripsi.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/pdf")
def export_pdf(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Export project content as PDF via LibreOffice headless."""
    project, sections, citations, pedoman = _get_project_data(project_id, current_user.id, db)

    try:
        docx_bytes = build_docx_document(
            project=project,
            sections=sections,
            citations=citations,
            pedoman=pedoman,
        )
        pdf_bytes = convert_docx_to_pdf(docx_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )

    filename = f"{project.title.replace(' ', '_')[:30]}_skripsi.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
