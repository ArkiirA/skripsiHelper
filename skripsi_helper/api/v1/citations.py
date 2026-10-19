import os
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from skripsi_helper.db.session import get_session
from skripsi_helper.models.user import User
from skripsi_helper.models.skripsi import SkripsiProject
from skripsi_helper.models.citation import Citation, UploadedPdf
from skripsi_helper.models.schema import CitationOut, CitationCreateManual, DoiLookupRequest
from skripsi_helper.api.v1.auth import get_current_user
from skripsi_helper.services.storage import store_pdf_file, get_pdf_download_url
from skripsi_helper.services.citation_extractor import (
    run_extraction_pipeline,
    lookup_crossref,
    format_citation_string,
)
from skripsi_helper.services.bibliography import build_bibliography

router = APIRouter(tags=["citations"])


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


@router.post("/projects/{project_id}/citations/upload", response_model=CitationOut, status_code=status.HTTP_201_CREATED)
async def upload_pdf_citation(
    project_id: int,
    file: UploadFile = File(...),
    section_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Upload PDF paper, store in GCS, run extraction pipeline, and return citation."""
    verify_project_ownership(project_id, current_user.id, db)

    pdf_bytes = await file.read()
    if not pdf_bytes or len(pdf_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or empty PDF file",
        )

    # 1. Store in GCS / Local fallback
    storage_path = store_pdf_file(pdf_bytes, file.filename or "paper.pdf", project_id)

    # 2. Extract metadata
    extraction = run_extraction_pipeline(pdf_bytes, file.filename or "paper.pdf")

    # 3. Create UploadedPdf record
    uploaded_pdf = UploadedPdf(
        skripsi_project_id=project_id,
        section_id=section_id,
        filename=file.filename or "paper.pdf",
        gcs_path=storage_path,
        file_size=len(pdf_bytes),
        mime_type=file.content_type or "application/pdf",
        extracted_doi=extraction.get("doi"),
        is_processed=True,
    )
    db.add(uploaded_pdf)
    db.commit()
    db.refresh(uploaded_pdf)

    # 4. Create Citation record
    citation = Citation(
        skripsi_project_id=project_id,
        section_id=section_id,
        uploaded_pdf_id=uploaded_pdf.id,
        title=extraction.get("title", "Untitled"),
        authors=extraction.get("authors", []),
        year=extraction.get("year"),
        journal=extraction.get("journal"),
        volume=extraction.get("volume"),
        issue=extraction.get("issue"),
        pages=extraction.get("pages"),
        doi=extraction.get("doi"),
        url=extraction.get("url"),
        citation_string=extraction.get("citation_string") or "Untitled",
        citation_style="apa",
        is_manual=False,
        needs_manual_completion=extraction.get("needs_manual_completion", False),
        source=extraction.get("source", "auto"),
    )
    db.add(citation)
    db.commit()
    db.refresh(citation)

    return citation


@router.post("/projects/{project_id}/citations/doi", response_model=CitationOut, status_code=status.HTTP_201_CREATED)
def lookup_citation_by_doi(
    project_id: int,
    req: DoiLookupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Lookup citation via DOI string directly."""
    verify_project_ownership(project_id, current_user.id, db)

    meta = lookup_crossref(req.doi)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DOI {req.doi} not found in CrossRef",
        )

    meta["citation_string"] = format_citation_string(meta)

    citation = Citation(
        skripsi_project_id=project_id,
        section_id=req.section_id,
        title=meta.get("title", "Untitled"),
        authors=meta.get("authors", []),
        year=meta.get("year"),
        journal=meta.get("journal"),
        volume=meta.get("volume"),
        issue=meta.get("issue"),
        pages=meta.get("pages"),
        doi=meta.get("doi", req.doi),
        url=meta.get("url"),
        citation_string=meta.get("citation_string"),
        citation_style="apa",
        is_manual=False,
        needs_manual_completion=False,
        source="doi_lookup",
    )
    db.add(citation)
    db.commit()
    db.refresh(citation)
    return citation


@router.post("/projects/{project_id}/citations/manual", response_model=CitationOut, status_code=status.HTTP_201_CREATED)
def create_manual_citation(
    project_id: int,
    manual_in: CitationCreateManual,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Create or manually complete a citation."""
    verify_project_ownership(project_id, current_user.id, db)

    meta_dict = manual_in.model_dump()
    citation_str = format_citation_string(meta_dict, style=manual_in.citation_style or "apa")

    citation = Citation(
        skripsi_project_id=project_id,
        section_id=manual_in.section_id,
        title=manual_in.title,
        authors=manual_in.authors,
        year=manual_in.year,
        journal=manual_in.journal,
        volume=manual_in.volume,
        issue=manual_in.issue,
        pages=manual_in.pages,
        doi=manual_in.doi,
        url=manual_in.url,
        citation_string=citation_str,
        citation_style=manual_in.citation_style or "apa",
        is_manual=True,
        needs_manual_completion=False,
        source="manual",
    )
    db.add(citation)
    db.commit()
    db.refresh(citation)
    return citation


@router.get("/projects/{project_id}/citations", response_model=List[CitationOut])
def list_project_citations(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List citations for a project."""
    verify_project_ownership(project_id, current_user.id, db)

    citations = db.execute(
        select(Citation)
        .where(Citation.skripsi_project_id == project_id)
        .order_by(Citation.created_at.desc())
    ).scalars().all()
    return citations


@router.get("/projects/{project_id}/bibliography")
def get_project_bibliography(
    project_id: int,
    style: Optional[str] = "apa",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Generate ordered Daftar Pustaka formatted for pedoman citation style."""
    verify_project_ownership(project_id, current_user.id, db)

    citations = db.execute(
        select(Citation)
        .where(Citation.skripsi_project_id == project_id)
        .order_by(Citation.created_at.asc())
    ).scalars().all()

    # Convert to dict representation
    citations_data = [
        {
            "id": c.id,
            "title": c.title,
            "authors": c.authors,
            "year": c.year,
            "journal": c.journal,
            "volume": c.volume,
            "issue": c.issue,
            "pages": c.pages,
            "doi": c.doi,
            "url": c.url,
        }
        for c in citations
    ]

    return build_bibliography(citations_data, style=style or "apa")


@router.get("/citations/{citation_id}/download")
def get_citation_pdf_download(
    citation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get download URL for a cited PDF paper."""
    citation = db.execute(
        select(Citation)
        .join(SkripsiProject)
        .where(Citation.id == citation_id)
        .where(SkripsiProject.user_id == current_user.id)
    ).scalar_one_or_none()

    if not citation or getattr(citation, "uploaded_pdf_id", None) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citation or linked PDF not found",
        )

    pdf = db.execute(
        select(UploadedPdf).where(UploadedPdf.id == citation.uploaded_pdf_id)
    ).scalar_one_or_none()

    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF record not found",
        )

    download_url = get_pdf_download_url(str(pdf.gcs_path))
    return {"download_url": download_url, "filename": str(pdf.filename)}


@router.get("/api/v1/citations/download-file")
def download_local_pdf(path: str):
    """Fallback download for local storage mode."""
    if not os.path.exists(path) or not path.startswith("storage/"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path, media_type="application/pdf")
