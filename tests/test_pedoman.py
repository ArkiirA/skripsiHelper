from fastapi.testclient import TestClient
from fastapi import status

from skripsi_helper.api.main import app
from skripsi_helper.api.v1 import pedoman

app.include_router(pedoman.router)


def test_create_pedoman_preset_unauthorized():
    """Create pedoman preset without token returns 401."""
    client = TestClient(app)
    response = client.post(
        "/pedoman/",
        json={"name": "Test Preset", "university_id": 1},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
