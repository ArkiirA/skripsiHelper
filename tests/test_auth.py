from fastapi.testclient import TestClient

from skripsi_helper.api.main import app
from skripsi_helper.api.v1 import auth

app.include_router(auth.router)


def test_get_current_user_invalid_token():
    """Get current user rejects invalid token."""
    client = TestClient(app)
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


def test_get_current_user_no_token():
    """Get current user rejects missing token."""
    client = TestClient(app)
    response = client.get("/auth/me")
    assert response.status_code == 401
