from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.config import load_auth_config
from app.tokens import (
    create_access_token,
    create_refresh_token,
    revoke_refresh_token,
    verify_access_token,
    verify_refresh_token,
)


def _decode(token: str) -> dict:
    return jwt.decode(token, load_auth_config()["JWT_SECRET_KEY"], algorithms=["HS256"])


def test_access_token_round_trip():
    token = create_access_token(42, "member")

    assert verify_access_token(token) == 42


def test_access_token_embeds_role_claim():
    # app/auth.py (the photo-viewer, a separate service with no DB of its
    # own) trusts this claim directly rather than re-querying a users
    # table - see documentation/tags/SCHEMA.md's role-visibility note.
    token = create_access_token(42, "admin")

    assert _decode(token)["role"] == "admin"


def test_refresh_token_round_trip(redis_client):
    token = create_refresh_token(42, redis_client=redis_client)

    user_id, jti = verify_refresh_token(token, redis_client=redis_client)

    assert user_id == 42
    assert isinstance(jti, str)


def test_access_token_wrong_type_is_rejected(redis_client):
    refresh_token = create_refresh_token(42, redis_client=redis_client)

    with pytest.raises(jwt.InvalidTokenError):
        verify_access_token(refresh_token)


def test_refresh_token_wrong_type_is_rejected():
    access_token = create_access_token(42, "member")

    with pytest.raises(jwt.InvalidTokenError):
        verify_refresh_token(access_token, redis_client=None)


def test_access_token_expires_after_its_ttl():
    now = datetime.now(timezone.utc) - timedelta(minutes=16)
    token = create_access_token(42, "member", now=now)

    with pytest.raises(jwt.ExpiredSignatureError):
        verify_access_token(token)


def test_refresh_token_expires_after_its_ttl(redis_client):
    now = datetime.now(timezone.utc) - timedelta(hours=13)
    token = create_refresh_token(42, redis_client=redis_client, now=now)

    with pytest.raises(jwt.ExpiredSignatureError):
        verify_refresh_token(token, redis_client=redis_client)


def test_revoked_refresh_token_is_rejected(redis_client):
    token = create_refresh_token(42, redis_client=redis_client)
    _, jti = verify_refresh_token(token, redis_client=redis_client)

    revoke_refresh_token(jti, redis_client=redis_client)

    with pytest.raises(jwt.InvalidTokenError):
        verify_refresh_token(token, redis_client=redis_client)
