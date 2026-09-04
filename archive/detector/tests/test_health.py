from fastapi.testclient import TestClient

from detector.main import app

client = TestClient(app)


def test_health_returns_ok():
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
