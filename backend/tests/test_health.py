from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify that GET /api/health returns 200 and {'status': 'ok'}."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    """Verify root endpoint responds with metadata."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PlanetPulse API is running" in response.json()["message"]
