import secrets
from dataclasses import dataclass

import psycopg

from app.security import hash_password


def create_account(conn: psycopg.Connection, *, email: str, password: str, role: str) -> tuple[int, str]:
    # Opaque, not human-chosen - see documentation/GLOSSARY.md's "Opaque
    # token" entry. 16 bytes / 32 hex chars, same margin as tokens.py's jti.
    username = secrets.token_hex(16)
    row = conn.execute(
        """
        INSERT INTO users (email, username, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (email, username, hash_password(password), role),
    ).fetchone()
    return row[0], username


@dataclass
class UserRecord:
    id: int
    email: str
    username: str
    password_hash: str
    role: str


def get_user_by_email(conn: psycopg.Connection, email: str) -> UserRecord | None:
    row = conn.execute(
        "SELECT id, email, username, password_hash, role FROM users WHERE email = %s",
        (email,),
    ).fetchone()
    if row is None:
        return None
    return UserRecord(id=row[0], email=row[1], username=row[2], password_hash=row[3], role=row[4])


def get_user_by_id(conn: psycopg.Connection, user_id: int) -> UserRecord | None:
    row = conn.execute(
        "SELECT id, email, username, password_hash, role FROM users WHERE id = %s",
        (user_id,),
    ).fetchone()
    if row is None:
        return None
    return UserRecord(id=row[0], email=row[1], username=row[2], password_hash=row[3], role=row[4])
