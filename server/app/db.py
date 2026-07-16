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
    committing test data permanently into the disposable test database.

    Deliberately does NOT auto-commit on a clean return: when a route
    raises HTTPException (e.g. a failed-login response), that exception
    is thrown into this generator at the `yield` line, so an auto-commit
    placed after it would never run - silently dropping any writes made
    before the raise (e.g. the failed-login audit_log row). Callers
    commit explicitly at the point they need a write to persist, same
    convention as scripts/create_account.py.
    """
    conn = get_connection()
    try:
        yield conn
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
    # Pulled forward from Phase 2's schema - TODO.md 1.7 needs it already.
    # user_id is nullable: a failed login by an unknown email has no user
    # to attach the row to.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(id),
            action TEXT NOT NULL,
            catalogue TEXT,
            filename TEXT,
            details JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
