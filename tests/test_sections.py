from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app

client = TestClient(app)


def test_get_section_unauthorized():
    """Accessing section without auth returns 401."""
    response = client.get("/sections/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_patch_section_unauthorized():
    """Updating section without auth returns 401."""
    response = client.patch(
        "/sections/1",
        json={"content": {"type": "doc", "content": []}, "word_count": 0},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
