import secrets
from dataclasses import dataclass

import psycopg

from app.security import hash_password


def create_account(
    conn: psycopg.Connection, *, email: str, password: str, role: str, invites_remaining: int = 0
) -> tuple[int, str]:
    # Opaque, not human-chosen - see documentation/GLOSSARY.md's "Opaque
    # token" entry. 16 bytes / 32 hex chars, same margin as tokens.py's jti.
    username = secrets.token_hex(16)
    row = conn.execute(
        """
        INSERT INTO users (email, username, password_hash, role, invites_remaining)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (email, username, hash_password(password), role, invites_remaining),
    ).fetchone()
    return row[0], username


@dataclass
class UserRecord:
    id: int
    email: str
    username: str
    password_hash: str
    role: str
    invites_remaining: int


_USER_COLUMNS = "id, email, username, password_hash, role, invites_remaining"


def get_user_by_email(conn: psycopg.Connection, email: str) -> UserRecord | None:
    row = conn.execute(
        f"SELECT {_USER_COLUMNS} FROM users WHERE email = %s",
        (email,),
    ).fetchone()
    if row is None:
        return None
    return UserRecord(*row)


def get_user_by_id(conn: psycopg.Connection, user_id: int) -> UserRecord | None:
    row = conn.execute(
        f"SELECT {_USER_COLUMNS} FROM users WHERE id = %s",
        (user_id,),
    ).fetchone()
    if row is None:
        return None
    return UserRecord(*row)
