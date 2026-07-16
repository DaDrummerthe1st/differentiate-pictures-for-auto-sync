from collections.abc import Iterator

import psycopg

from app.config import load_db_config


def get_connection() -> psycopg.Connection:
    config = load_db_config()
    return psycopg.connect(
        host=config["POSTGRES_HOST"],
        port=config["POSTGRES_PORT"],
        dbname=config["POSTGRES_DB"],
        user=config["POSTGRES_USER"],
        password=config["POSTGRES_PASSWORD"],
    )


def get_db() -> Iterator[psycopg.Connection]:
    """FastAPI dependency wrapping get_connection() - overridden in tests
    (see tests/conftest.py) to reuse the test's own connection/transaction
    instead of opening a second one, so seeded rows are visible without
    committing test data permanently into the disposable test database."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_schema(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
