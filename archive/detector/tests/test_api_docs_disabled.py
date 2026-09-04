from fastapi.testclient import TestClient

from detector.main import app

client = TestClient(app)

DOC_PATHS = ["/docs", "/redoc", "/openapi.json"]


def test_docs_routes_do_not_exist():
    # Same bar as app/'s own docs_url=None (app/tests/test_api_docs_disabled.py) -
    # this service is internal-network-only (no host port published), but
    # disabling the auto-generated schema/docs endpoints is still cheap
    # and avoids exposing internal implementation detail to anything else
    # on the compose network.
    for path in DOC_PATHS:
        res = client.get(path)
        assert res.status_code == 404, path
