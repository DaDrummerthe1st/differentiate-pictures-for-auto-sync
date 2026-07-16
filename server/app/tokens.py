import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum

import jwt
import redis

from app.config import load_auth_config

# A private, two-account family server doesn't need buzzkit's 30-day
# "remember me" refresh window - short-lived by design so a stolen
# cookie has a small blast radius.
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_HOURS = 12

_JWT_ALGORITHM = "HS256"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(load_auth_config()["REDIS_URL"])


def _encode(payload: dict) -> str:
    return jwt.encode(payload, load_auth_config()["JWT_SECRET_KEY"], algorithm=_JWT_ALGORITHM)


def _decode(token: str) -> dict:
    return jwt.decode(token, load_auth_config()["JWT_SECRET_KEY"], algorithms=[_JWT_ALGORITHM])


def create_access_token(user_id: int, *, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": TokenType.ACCESS,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(uuid.uuid4()),
    }
    return _encode(payload)


def verify_access_token(token: str) -> int:
    payload = _decode(token)
    if payload.get("type") != TokenType.ACCESS:
        raise jwt.InvalidTokenError("wrong token type")
    return int(payload["sub"])


def create_refresh_token(
    user_id: int, *, redis_client: redis.Redis, now: datetime | None = None
) -> str:
    now = now or datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    ttl = timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "type": TokenType.REFRESH,
        "iat": now,
        "exp": now + ttl,
        "jti": jti,
    }
    # Refresh tokens are allowlisted in Redis so logout/rotation can
    # revoke one before its natural expiry - a bare JWT can't be
    # invalidated early otherwise.
    redis_client.set(f"refresh_token:{jti}", str(user_id), ex=int(ttl.total_seconds()))
    return _encode(payload)


def verify_refresh_token(token: str, *, redis_client: redis.Redis | None) -> tuple[int, str]:
    payload = _decode(token)
    if payload.get("type") != TokenType.REFRESH:
        raise jwt.InvalidTokenError("wrong token type")
    jti = payload["jti"]
    stored_user_id = redis_client.get(f"refresh_token:{jti}")
    if stored_user_id is None:
        raise jwt.InvalidTokenError("refresh token revoked or expired")
    return int(payload["sub"]), jti


def revoke_refresh_token(jti: str, *, redis_client: redis.Redis) -> None:
    redis_client.delete(f"refresh_token:{jti}")
