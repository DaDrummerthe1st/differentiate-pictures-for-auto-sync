DOC_PATHS = ["/docs", "/redoc", "/openapi.json"]


def test_docs_routes_do_not_exist(client):
    for path in DOC_PATHS:
        res = client.get(path)
        assert res.status_code == 404, path
