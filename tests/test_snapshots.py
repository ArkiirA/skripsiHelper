from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app

client = TestClient(app)


def test_list_snapshots_unauthorized():
    """Listing snapshots without auth returns 401."""
    response = client.get("/sections/1/snapshots")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_snapshot_unauthorized():
    """Previewing snapshot without auth returns 401."""
    response = client.get("/snapshots/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_restore_snapshot_unauthorized():
    """Restoring snapshot without auth returns 401."""
    response = client.post("/snapshots/1/restore")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
