import os
import time

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import ACCESS_COOKIE, require_session_with_role

_SECRET = os.environ["JWT_SECRET_KEY"]

# A throwaway probe app, not app.main - this tests require_session_with_role
# in isolation, independent of any route that ends up calling it.
_probe_app = FastAPI()


@_probe_app.get("/_probe")
def _probe(session: tuple[int, str] = Depends(require_session_with_role)):
    user_id, role = session
    return {"user_id": user_id, "role": role}


@pytest.fixture()
def client():
    with TestClient(_probe_app) as test_client:
        yield test_client


def _token(*, role: str | None = "member", secret: str = _SECRET) -> str:
    now = int(time.time())
    payload = {"sub": "7", "type": "access", "iat": now, "exp": now + 900, "jti": "probe-jti"}
    if role is not None:
        payload["role"] = role
    return jwt.encode(payload, secret, algorithm="HS256")


def test_returns_user_id_and_role_from_token(client):
    client.cookies.set(ACCESS_COOKIE, _token(role="admin"))

    res = client.get("/_probe")

    assert res.status_code == 200
    assert res.json() == {"user_id": 7, "role": "admin"}


def test_missing_role_claim_defaults_to_member_not_admin(client):
    # Old-style tokens minted before this session's change carry no role
    # claim at all - fail closed (member), never silently elevate.
    client.cookies.set(ACCESS_COOKIE, _token(role=None))

    res = client.get("/_probe")

    assert res.status_code == 200
    assert res.json()["role"] == "member"


def test_tampered_signature_is_rejected_even_with_an_admin_role_claim(client):
    client.cookies.set(ACCESS_COOKIE, _token(role="admin", secret="a-completely-different-secret-32ch"))

    res = client.get("/_probe")

    assert res.status_code == 401


def test_missing_cookie_returns_401(client):
    res = client.get("/_probe")

    assert res.status_code == 401
