from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app
from skripsi_helper.api.v1 import projects

app.include_router(projects.router)


def test_create_project_unauthorized():
    """Create project without token returns 401."""
    client = TestClient(app)
    response = client.post(
        "/projects/",
        json={"title": "Test Skripsi", "topic": "Machine Learning", "pedoman_preset_id": 1},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_projects_unauthorized():
    """List projects without token returns 401."""
    client = TestClient(app)
    response = client.get("/projects/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_project_unauthorized():
    """Get project without token returns 401."""
    client = TestClient(app)
    response = client.get("/projects/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
