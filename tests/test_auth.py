import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from skripsi_helper.api.main import app
from skripsi_helper.api.v1 import auth

app.include_router(auth.router)


def test_google_login_raises_not_implemented():
    """Google login endpoint raises NotImplementedError."""
    client = TestClient(app)
    with pytest.raises(NotImplementedError):
        client.get("/auth/google/login")


def test_oauth_callback_raises_not_implemented():
    """OAuth callback endpoint raises NotImplementedError."""
    client = TestClient(app)
    with pytest.raises(NotImplementedError):
        client.get("/auth/callback?code=test")


def test_get_current_user_raises_not_implemented():
    """Get current user endpoint raises NotImplementedError."""
    client = TestClient(app)
    # oauth2_scheme validates token first, then endpoint raises NotImplementedError
    # Token validation fails first, but endpoint still raises NotImplementedError
    with pytest.raises(NotImplementedError):
        client.get("/auth/me", headers={"Authorization": "Bearer test"})
