import jwt
import psycopg
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.accounts import UserRecord, get_user_by_email
from app.audit import log_audit_event
from app.cookies import ACCESS_COOKIE, set_auth_cookies
from app.db import get_db
from app.rate_limit import limiter
from app.security import hash_password, verify_password
from app.tokens import create_access_token, create_refresh_token, get_redis_client, verify_access_token

router = APIRouter()

_GENERIC_LOGIN_ERROR = "Incorrect email or password"

# Precomputed once so an unknown email still pays the same argon2 verify
# cost as a real one - otherwise a short-circuited "no such user" response
# would be measurably faster than "wrong password", disclosing which
# emails are registered (TODO.md 1.4).
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-safety")


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    email: str
    role: str


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: psycopg.Connection = Depends(get_db),
):
    user = get_user_by_email(db, payload.email)
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, password_hash)

    if user is None or not password_ok:
        log_audit_event(
            db,
            action="login_failure",
            user_id=user.id if user is not None else None,
            details={"attempted_email": payload.email},
        )
        # commit explicitly: get_db() does not auto-commit on an
        # exception path, and HTTPException below would otherwise
        # discard this audit row along with it.
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, _GENERIC_LOGIN_ERROR)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id, redis_client=get_redis_client())
    set_auth_cookies(response, access_token, refresh_token)

    log_audit_event(db, action="login_success", user_id=user.id)
    db.commit()

    return LoginResponse(email=user.email, role=user.role)


def get_current_user(
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE),
    db: psycopg.Connection = Depends(get_db),
) -> UserRecord:
    if access_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        user_id = verify_access_token(access_token)
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")

    user = db.execute(
        "SELECT id, email, password_hash, role FROM users WHERE id = %s",
        (user_id,),
    ).fetchone()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    return UserRecord(id=user[0], email=user[1], password_hash=user[2], role=user[3])


@router.get("/whoami", response_model=LoginResponse)
def whoami(user: UserRecord = Depends(get_current_user)) -> LoginResponse:
    return LoginResponse(email=user.email, role=user.role)
