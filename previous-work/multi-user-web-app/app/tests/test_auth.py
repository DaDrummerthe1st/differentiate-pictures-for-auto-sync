import os
import time

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import ACCESS_COOKIE, require_session_with_username

_SECRET = os.environ["JWT_SECRET_KEY"]

# A throwaway probe app, not app.main - this tests require_session_with_username
# in isolation, independent of any route that ends up calling it.
_probe_app = FastAPI()


@_probe_app.get("/_probe")
def _probe(session: tuple[int, str] = Depends(require_session_with_username)):
    user_id, username = session
    return {"user_id": user_id, "username": username}


@pytest.fixture()
def client():
    with TestClient(_probe_app) as test_client:
        yield test_client


def _token(*, username: str | None = "opaquetoken123", secret: str = _SECRET) -> str:
    now = int(time.time())
    payload = {"sub": "7", "type": "access", "iat": now, "exp": now + 900, "jti": "probe-jti"}
    if username is not None:
        payload["username"] = username
    return jwt.encode(payload, secret, algorithm="HS256")


def test_returns_user_id_and_username_from_token(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaquetoken123"))

    res = client.get("/_probe")

    assert res.status_code == 200
    assert res.json() == {"user_id": 7, "username": "opaquetoken123"}


def test_missing_username_claim_is_rejected(client):
    # Unlike role (which has a safe "member" default), there's no safe
    # default storage folder to fall back to - a token minted before the
    # username claim existed (or one that omits it) must fail closed
    # (401), never fall back to something guessable like the numeric
    # user id.
    client.cookies.set(ACCESS_COOKIE, _token(username=None))

    res = client.get("/_probe")

    assert res.status_code == 401


def test_tampered_signature_is_rejected_even_with_a_username_claim(client):
    client.cookies.set(ACCESS_COOKIE, _token(username="opaquetoken123", secret="a-completely-different-secret-32ch"))

    res = client.get("/_probe")

    assert res.status_code == 401


def test_missing_cookie_returns_401(client):
    res = client.get("/_probe")

    assert res.status_code == 401
