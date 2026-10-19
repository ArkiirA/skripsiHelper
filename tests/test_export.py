"""Tests for export functionality (DOCX + PDF)."""
import io
import tempfile
from pathlib import Path

from skripsi_helper.services.export import build_docx_document, convert_docx_to_pdf


def test_build_docx_document_minimal():
    """Build minimal DOCX without citations or pedoman."""
    # Create minimal mock objects
    class MockProject:
        title = "Test Skripsi"

    class MockSection:
        def __init__(self, title, order, content=None):
            self.title = title
            self.order = order
            self.content = content or {}

    class MockCitation:
        citation_string = "Test Citation"

    sections = [
        MockSection("BAB I", 1, {"content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test content"}]}]}),
    ]
    citations = [MockCitation()]

    docx_bytes = build_docx_document(
        project=MockProject(),
        sections=sections,
        citations=citations,
    )

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0
    # DOCX files are ZIP archives - check for DOCX signature
    assert docx_bytes[:4] == b"PK\x03\x04" or docx_bytes[:2] == b"PK"


def test_build_docx_with_citations():
    """Build DOCX with citation strings."""
    class MockProject:
        title = " Thesis with Citations "

    class MockSection:
        title = "Chapter 1"
        order = 1
        content = {"content": []}

    class MockCitation:
        citation_string = "Smith, J. (2023). Test Paper. Journal of Tests."

    sections = [MockSection()]
    citations = [MockCitation()]

    docx_bytes = build_docx_document(
        project=MockProject(),
        sections=sections,
        citations=citations,
    )

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0


def test_build_docx_with_pedoman():
    """Build DOCX with custom pedoman settings."""
    class MockProject:
        title = "Test"

    class MockSection:
        title = "Sec"
        order = 1
        content = {}

    class MockPedoman:
        default_margins = {"top": 2.5, "bottom": 2.5, "left": 4.0, "right": 3.0}
        default_font = "Times New Roman"
        default_font_size = 12
        default_line_spacing = 1.5

    sections = [MockSection()]
    citations = []

    docx_bytes = build_docx_document(
        project=MockProject(),
        sections=sections,
        citations=citations,
        pedoman=MockPedoman(),
    )

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 0


def test_convert_to_pdf():
    """Convert DOCX to PDF using LibreOffice."""
    # Create a minimal DOCX in memory
    class MockProject:
        title = "Test"

    class MockSection:
        title = "Sec"
        order = 1
        content = {}

    docx_bytes = build_docx_document(
        project=MockProject(),
        sections=[MockSection()],
        citations=[],
    )

    # Convert to PDF
    pdf_bytes = convert_docx_to_pdf(docx_bytes)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF files start with %PDF-
    assert pdf_bytes[:5] == b"%PDF-"
