import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import psycopg

from app.accounts import create_account

# 16 bytes / ~22 url-safe chars - same entropy margin as accounts.py's
# username token, unguessable enough that a token doesn't need any
# additional rate-limiting to resist brute-forcing.
INVITE_TOKEN_BYTES = 16
INVITE_EXPIRE_DAYS = 7

_INVITE_COLUMNS = (
    "id, token, inviter_id, invitee_email, granted_invites, status, accepted_user_id, "
    "created_at, expires_at"
)


@dataclass
class InviteRecord:
    id: int
    token: str
    inviter_id: int
    invitee_email: str
    granted_invites: int
    status: str
    accepted_user_id: int | None
    created_at: datetime
    expires_at: datetime


def create_invite(
    conn: psycopg.Connection,
    *,
    inviter_id: int,
    invitee_email: str,
    granted_invites: int = 0,
    now: datetime | None = None,
) -> InviteRecord:
    now = now or datetime.now(timezone.utc)
    token = secrets.token_urlsafe(INVITE_TOKEN_BYTES)
    expires_at = now + timedelta(days=INVITE_EXPIRE_DAYS)
    row = conn.execute(
        f"""
        INSERT INTO invites (token, inviter_id, invitee_email, granted_invites, status, created_at, expires_at)
        VALUES (%s, %s, %s, %s, 'pending', %s, %s)
        RETURNING {_INVITE_COLUMNS}
        """,
        (token, inviter_id, invitee_email, granted_invites, now, expires_at),
    ).fetchone()
    return InviteRecord(*row)


def get_invite_by_token(conn: psycopg.Connection, token: str) -> InviteRecord | None:
    row = conn.execute(
        f"SELECT {_INVITE_COLUMNS} FROM invites WHERE token = %s",
        (token,),
    ).fetchone()
    if row is None:
        return None
    return InviteRecord(*row)


def accept_invite(
    conn: psycopg.Connection, *, invite: InviteRecord, password: str
) -> tuple[int, str]:
    """Creates the invited account (always role=member - only
    create_account.py's own CLI path can mint an admin, see
    documentation/GLOSSARY.md's "Invite delegation" entry) and marks the
    invite accepted. Caller must already have checked status/expiry - this
    performs the two writes without re-checking either."""
    user_id, username = create_account(
        conn,
        email=invite.invitee_email,
        password=password,
        role="member",
        invites_remaining=invite.granted_invites,
    )
    conn.execute(
        "UPDATE invites SET status = 'accepted', accepted_user_id = %s WHERE id = %s",
        (user_id, invite.id),
    )
    return user_id, username
