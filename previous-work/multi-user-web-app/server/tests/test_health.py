from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_response_body_has_no_version_or_stack_info():
    response = client.get("/health")

    assert response.json() == {"status": "ok"}
