from fastapi.testclient import TestClient

from skripsi_helper.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SkripsiHelper API"
    assert data["version"] == "0.1.0"
