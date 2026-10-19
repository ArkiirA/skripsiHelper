import io
import fitz
from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app
from skripsi_helper.services.citation_extractor import (
    extract_doi_from_pdf,
    format_citation_string,
    run_extraction_pipeline,
)

client = TestClient(app)


def create_dummy_pdf(text: str = "Test document") -> bytes:
    """Create in-memory PDF for tests."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_format_citation_string_apa():
    meta = {
        "title": "Machine Learning in Higher Education",
        "authors": [{"name": "Santoso, B."}, {"name": "Pratama, A."}],
        "year": 2024,
        "journal": "Jurnal Ilmu Komputer",
        "doi": "10.1234/jik.2024.01",
    }
    result = format_citation_string(meta, style="apa")
    assert "Santoso, B. & Pratama, A." in result
    assert "(2024)" in result
    assert "Machine Learning in Higher Education" in result
    assert "https://doi.org/10.1234/jik.2024.01" in result


def test_extract_doi_from_pdf_text():
    sample_text = "Journal of AI Research. DOI: 10.1016/j.artint.2023.103982. Published online."
    pdf_bytes = create_dummy_pdf(sample_text)
    doi = extract_doi_from_pdf(pdf_bytes)
    assert doi == "10.1016/j.artint.2023.103982"


def test_extraction_pipeline_fallback():
    pdf_bytes = create_dummy_pdf("Dokumen skripsi tanpa metadata atau DOI tertentu.")
    result = run_extraction_pipeline(pdf_bytes, "skripsi_mahasiswa.pdf")
    assert result["needs_manual_completion"] is True
    assert "skripsi mahasiswa" in result["title"].lower()


def test_upload_citation_unauthorized():
    dummy_pdf = io.BytesIO(create_dummy_pdf())
    response = client.post(
        "/projects/1/citations/upload",
        files={"file": ("test.pdf", dummy_pdf, "application/pdf")},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_lookup_doi_unauthorized():
    response = client.post(
        "/projects/1/citations/doi",
        json={"doi": "10.1016/j.artint.2023.103982"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_manual_citation_unauthorized():
    response = client.post(
        "/projects/1/citations/manual",
        json={
            "title": "Metode Penelitian Kualitatif",
            "authors": [{"name": "Sugiyono"}],
            "year": 2020,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_citations_unauthorized():
    response = client.get("/projects/1/citations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_download_citation_pdf_unauthorized():
    response = client.get("/citations/1/download")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
