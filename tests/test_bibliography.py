from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app
from skripsi_helper.services.bibliography import (
    format_inline_marker,
    format_bibliography_entry,
    build_bibliography,
)

client = TestClient(app)

SAMPLE_CITATIONS = [
    {
        "id": 1,
        "title": "Analisis Sentimen Twitter dengan BERT",
        "authors": [{"name": "Pratama, Budi"}],
        "year": 2023,
        "journal": "Jurnal Sains Komputer",
        "volume": "10",
        "issue": "2",
        "pages": "100-112",
        "doi": "10.1234/jsk.2023.01",
    },
    {
        "id": 2,
        "title": "Penerapan Deep Learning pada Pengolahan Citra Medis",
        "authors": [{"name": "Aditya, Rizky"}, {"name": "Lestari, Dewi"}],
        "year": 2022,
        "journal": "Informatika Indonesia",
        "volume": "15",
        "issue": "1",
        "pages": "45-52",
        "doi": "10.1234/ii.2022.02",
    },
]


def test_format_apa():
    inline = format_inline_marker(SAMPLE_CITATIONS[0], index=1, style="apa")
    assert inline == "(Pratama, 2023)"

    inline_two = format_inline_marker(SAMPLE_CITATIONS[1], index=2, style="apa")
    assert inline_two == "(Aditya & Lestari, 2022)"

    entry = format_bibliography_entry(SAMPLE_CITATIONS[0], index=1, style="apa")
    assert "Pratama, B. (2023)" in entry
    assert "Analisis Sentimen Twitter dengan BERT" in entry


def test_format_ieee():
    inline = format_inline_marker(SAMPLE_CITATIONS[0], index=1, style="ieee")
    assert inline == "[1]"

    entry = format_bibliography_entry(SAMPLE_CITATIONS[0], index=1, style="ieee")
    assert "[1] B. Pratama" in entry
    assert "Analisis Sentimen Twitter dengan BERT" in entry


def test_format_vancouver():
    inline = format_inline_marker(SAMPLE_CITATIONS[0], index=1, style="vancouver")
    assert inline == "[1]"

    entry = format_bibliography_entry(SAMPLE_CITATIONS[0], index=1, style="vancouver")
    assert "1. Pratama B. Analisis Sentimen Twitter dengan BERT" in entry


def test_format_harvard():
    inline = format_inline_marker(SAMPLE_CITATIONS[0], index=1, style="harvard")
    assert inline == "(Pratama 2023)"

    entry = format_bibliography_entry(SAMPLE_CITATIONS[0], index=1, style="harvard")
    assert "Pratama, B., 2023" in entry


def test_format_chicago():
    inline = format_inline_marker(SAMPLE_CITATIONS[0], index=1, style="chicago")
    assert inline == "(Pratama 2023)"

    entry = format_bibliography_entry(SAMPLE_CITATIONS[0], index=1, style="chicago")
    assert 'Pratama, Budi. 2023. "Analisis Sentimen Twitter dengan BERT."' in entry


def test_build_bibliography_sorting():
    # In APA style, Aditya (id 2) should be ordered before Pratama (id 1)
    res = build_bibliography(SAMPLE_CITATIONS, style="apa")
    assert res["total_citations"] == 2
    assert res["entries"][0]["id"] == 2
    assert res["entries"][1]["id"] == 1


def test_get_bibliography_unauthorized():
    response = client.get("/projects/1/bibliography")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
