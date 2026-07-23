import os

import jwt
from fastapi import HTTPException, Request

# Verifies the same HS256 access-token cookie issued by server/app's auth
# backend (server/app/tokens.py + server/app/cookies.py) - shared secret,
# no shared code deployment, since the two apps ship as separate images.
ACCESS_COOKIE = "photo_server_access"
_JWT_ALGORITHM = "HS256"

MIN_JWT_SECRET_KEY_LENGTH = 32


class MissingConfigError(RuntimeError):
    pass


def _jwt_secret_key() -> str:
    key = os.environ.get("JWT_SECRET_KEY")
    if not key:
        raise MissingConfigError("Missing required environment variable: JWT_SECRET_KEY")
    if len(key) < MIN_JWT_SECRET_KEY_LENGTH:
        raise MissingConfigError(
            f"JWT_SECRET_KEY must be at least {MIN_JWT_SECRET_KEY_LENGTH} characters"
        )
    return key


def load_auth_config() -> None:
    """Fail fast at startup if JWT_SECRET_KEY is missing/too short, rather
    than booting successfully and then 401-ing every request at runtime."""
    _jwt_secret_key()


def _decode_access_token(request: Request) -> dict | None:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        return None
    try:
        payload = jwt.decode(token, _jwt_secret_key(), algorithms=[_JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    if payload.get("type") != "access":
        return None
    return payload


def has_valid_session(request: Request) -> bool:
    """Like require_session, but for callers that want a redirect (e.g.
    the app shell route) instead of a 401 - never raises."""
    return _decode_access_token(request) is not None


def require_session(request: Request) -> int:
    payload = _decode_access_token(request)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return int(payload["sub"])
