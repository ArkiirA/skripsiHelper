"""Tests for dashboard/progress endpoint."""
from fastapi.testclient import TestClient

from skripsi_helper.api.main import app

client = TestClient(app)


def test_get_dashboard_returns_401_without_auth():
    """Dashboard requires authentication."""
    response = client.get("/projects/1/dashboard")
    assert response.status_code == 401


def test_get_dashboard_returns_401_or_404_with_invalid_token():
    """Invalid token returns 401."""
    response = client.get(
        "/projects/999/dashboard",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
