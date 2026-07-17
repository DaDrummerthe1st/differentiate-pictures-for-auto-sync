import os
import time

import jwt
import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-chars")

_SECRET = os.environ["JWT_SECRET_KEY"]

PROTECTED_GET_ROUTES = [
    ("/api/tree", {}),
    ("/api/file-summary", {}),
    ("/thumb", {"p": "AlbumA/1/pic1.jpg"}),
    ("/original", {"p": "AlbumA/1/pic1.jpg"}),
    ("/api/voiceovers", {}),
]


def _access_token(*, exp_offset: int = 900, token_type: str = "access") -> str:
    now = int(time.time())
    payload = {
        "sub": "1",
        "type": token_type,
        "iat": now,
        "exp": now + exp_offset,
        "jti": "test-jti",
    }
    return jwt.encode(payload, _SECRET, algorithm="HS256")


@pytest.mark.parametrize("path,params", PROTECTED_GET_ROUTES)
def test_protected_route_without_session_cookie_returns_401(client, path, params):
    client.cookies.delete("photo_server_access")
    res = client.get(path, params=params)
    assert res.status_code == 401


@pytest.mark.parametrize("path,params", PROTECTED_GET_ROUTES)
def test_protected_route_with_garbage_cookie_returns_401(client, path, params):
    client.cookies.set("photo_server_access", "not-a-real-token")
    res = client.get(path, params=params)
    assert res.status_code == 401


@pytest.mark.parametrize("path,params", PROTECTED_GET_ROUTES)
def test_protected_route_with_expired_token_returns_401(client, path, params):
    client.cookies.set("photo_server_access", _access_token(exp_offset=-10))
    res = client.get(path, params=params)
    assert res.status_code == 401


@pytest.mark.parametrize("path,params", PROTECTED_GET_ROUTES)
def test_protected_route_with_refresh_token_type_returns_401(client, path, params):
    # A refresh token must not authenticate access to protected routes -
    # only an access-type token should.
    client.cookies.set("photo_server_access", _access_token(token_type="refresh"))
    res = client.get(path, params=params)
    assert res.status_code == 401


@pytest.mark.parametrize("path,params", PROTECTED_GET_ROUTES)
def test_protected_route_with_valid_access_token_returns_200(client, path, params):
    client.cookies.set("photo_server_access", _access_token())
    res = client.get(path, params=params)
    assert res.status_code == 200
