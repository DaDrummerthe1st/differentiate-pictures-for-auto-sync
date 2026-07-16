from dataclasses import dataclass

import psycopg

from app.security import hash_password


def create_account(conn: psycopg.Connection, *, email: str, password: str, role: str) -> int:
    row = conn.execute(
        """
        INSERT INTO users (email, password_hash, role)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (email, hash_password(password), role),
    ).fetchone()
    return row[0]


@dataclass
class UserRecord:
    id: int
    email: str
    password_hash: str
    role: str


def get_user_by_email(conn: psycopg.Connection, email: str) -> UserRecord | None:
    row = conn.execute(
        "SELECT id, email, password_hash, role FROM users WHERE email = %s",
        (email,),
    ).fetchone()
    if row is None:
        return None
    return UserRecord(id=row[0], email=row[1], password_hash=row[2], role=row[3])
