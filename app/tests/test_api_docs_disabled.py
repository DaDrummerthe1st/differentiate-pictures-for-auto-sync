from app.auth import ACCESS_COOKIE

DOC_PATHS = ["/docs", "/redoc", "/openapi.json"]


def test_docs_routes_do_not_exist_for_an_anonymous_visitor(client):
    client.cookies.delete(ACCESS_COOKIE)
    for path in DOC_PATHS:
        res = client.get(path)
        assert res.status_code == 404, path


def test_docs_routes_do_not_exist_even_with_a_valid_session(client):
    # Not just auth-gated - the routes must not be registered at all,
    # so a logged-in session doesn't matter either.
    for path in DOC_PATHS:
        res = client.get(path)
        assert res.status_code == 404, path
