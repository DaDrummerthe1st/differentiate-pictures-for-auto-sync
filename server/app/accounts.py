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
