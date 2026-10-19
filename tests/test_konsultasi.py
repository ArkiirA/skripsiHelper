from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app

client = TestClient(app)


def test_create_konsultasi_log_unauthorized():
    """Creating a konsultasi log entry without auth returns 401."""
    response = client.post(
        "/projects/1/konsultasi",
        json={"notes": "Perbaiki bab 1 bagian latar belakang", "action_items": ["Cari 3 jurnal"]},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_konsultasi_logs_unauthorized():
    """Listing konsultasi logs without auth returns 401."""
    response = client.get("/projects/1/konsultasi")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_konsultasi_summary_unauthorized():
    """Getting konsultasi reminder summary without auth returns 401."""
    response = client.get("/projects/1/konsultasi/summary")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_toggle_konsultasi_resolved_unauthorized():
    """Toggling resolved status without auth returns 401."""
    response = client.patch("/konsultasi/1/toggle-resolved")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
