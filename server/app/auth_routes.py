import os
from datetime import datetime, timezone

import jwt
import psycopg
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.accounts import UserRecord, get_user_by_email, get_user_by_id
from app.audit import log_audit_event
from app.cookies import ACCESS_COOKIE, REFRESH_COOKIE, clear_auth_cookies, set_auth_cookies
from app.db import get_db
from app.invites import accept_invite, create_invite, get_invite_by_token
from app.mail import send_invite_email
from app.rate_limit import limiter
from app.security import hash_password, verify_password
from app.tokens import (
    create_access_token,
    create_refresh_token,
    get_redis_client,
    revoke_refresh_token,
    verify_access_token,
    verify_refresh_token,
)

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
    username: str


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

    access_token = create_access_token(user.id, user.role, user.username)
    refresh_token = create_refresh_token(user.id, redis_client=get_redis_client())
    set_auth_cookies(response, access_token, refresh_token)

    log_audit_event(db, action="login_success", user_id=user.id)
    db.commit()

    return LoginResponse(email=user.email, role=user.role, username=user.username)


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

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    return user


@router.get("/whoami", response_model=LoginResponse)
def whoami(user: UserRecord = Depends(get_current_user)) -> LoginResponse:
    return LoginResponse(email=user.email, role=user.role, username=user.username)


class MessageResponse(BaseModel):
    message: str


@router.post("/refresh", response_model=MessageResponse)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    db: psycopg.Connection = Depends(get_db),
):
    if refresh_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    redis_client = get_redis_client()
    try:
        user_id, jti = verify_refresh_token(refresh_token, redis_client=redis_client)
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")

    # Re-read role from the DB rather than carrying it forward from
    # whatever the old access token claimed - refresh is exactly the
    # moment a role change (or account deletion) should take effect,
    # same reasoning as the revocation-check bound noted in tokens.py.
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")

    # Rotate: the old refresh token is single-use, same as buzzkit's design.
    revoke_refresh_token(jti, redis_client=redis_client)
    new_access_token = create_access_token(user.id, user.role, user.username)
    new_refresh_token = create_refresh_token(user.id, redis_client=redis_client)
    set_auth_cookies(response, new_access_token, new_refresh_token)

    return MessageResponse(message="refreshed")


@router.post("/logout", response_model=MessageResponse)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
):
    if refresh_token is not None:
        try:
            _, jti = verify_refresh_token(refresh_token, redis_client=get_redis_client())
            revoke_refresh_token(jti, redis_client=get_redis_client())
        except jwt.InvalidTokenError:
            pass

    clear_auth_cookies(response)
    return MessageResponse(message="logged out")


class CreateInviteRequest(BaseModel):
    email: str
    # Only an admin caller may set this above 0 - see the role check
    # below. A member's own invite always starts the new account at 0
    # (no further delegation) unless an admin raises it later.
    granted_invites: int = 0


class InviteResponse(BaseModel):
    token: str
    invitee_email: str
    granted_invites: int
    expires_at: datetime


@router.post("/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def create_invite_route(
    payload: CreateInviteRequest,
    user: UserRecord = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
):
    if payload.granted_invites < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "granted_invites must not be negative")
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "That email already has an account")

    if user.role != "admin":
        if payload.granted_invites > 0:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only an admin can grant invite quota")
        # Atomic check-and-decrement (not a separate read then write) so
        # two concurrent invite requests from the same low-quota account
        # can't both pass a stale "remaining > 0" check.
        decremented = db.execute(
            "UPDATE users SET invites_remaining = invites_remaining - 1 WHERE id = %s AND invites_remaining > 0",
            (user.id,),
        )
        if decremented.rowcount == 0:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No invites remaining")

    invite = create_invite(
        db, inviter_id=user.id, invitee_email=payload.email, granted_invites=payload.granted_invites
    )
    log_audit_event(db, action="invite_created", user_id=user.id, details={"invitee_email": payload.email})
    db.commit()

    # Best-effort (app.mail's own doc) - the token returned below is a
    # complete fallback on its own, so a failed/skipped send never blocks
    # invite creation. APP_ORIGIN has the same "optional, defaults for
    # local/test" shape as SMTP_HOST - no local/dev/test environment sets
    # it, and every real deploy needs it set to https://photos.reuterborg.se.
    accept_url = f"{os.environ.get('APP_ORIGIN', 'http://localhost')}/accept-invite?token={invite.token}"
    send_invite_email(payload.email, accept_url)

    return InviteResponse(
        token=invite.token,
        invitee_email=invite.invitee_email,
        granted_invites=invite.granted_invites,
        expires_at=invite.expires_at,
    )


class AcceptInviteRequest(BaseModel):
    password: str


@router.post("/invites/{token}/accept", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def accept_invite_route(
    token: str,
    payload: AcceptInviteRequest,
    response: Response,
    db: psycopg.Connection = Depends(get_db),
):
    invite = get_invite_by_token(db, token)
    if invite is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")
    if invite.status != "pending":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invite already used")
    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invite expired")
    if get_user_by_email(db, invite.invitee_email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "That email already has an account")

    user_id, username = accept_invite(db, invite=invite, password=payload.password)
    log_audit_event(db, action="invite_accepted", user_id=user_id)
    db.commit()

    # Same as /login - accepting an invite logs the new account straight
    # in rather than making them immediately re-enter the password they
    # just chose.
    access_token = create_access_token(user_id, "member", username)
    refresh_token = create_refresh_token(user_id, redis_client=get_redis_client())
    set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(email=invite.invitee_email, role="member", username=username)
