import secrets
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
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    # Added for per-user storage-path scoping (dpfas_media/<username>/, see
    # documentation/plans/deep-singing-firefly.md) - an opaque random token,
    # not a real name (documentation/GLOSSARY.md's "Opaque token" entry).
    # ALTER ... IF NOT EXISTS is a no-op against the CREATE TABLE above on a
    # fresh install; against prod's already-existing, non-empty table this
    # raises NotNullViolation the first time (Postgres can't add a NOT NULL
    # column with no default against existing rows) - run
    # backfill_missing_usernames() below once, out of band, before this
    # ever runs against such a table. Not run destructively (accounts were
    # briefly deleted-and-recreated for this instead, 2026-08-13 - see
    # documentation/bugs/claude-bugs/fixed/2026-08-13-recommended-raw-destructive-sql-against-production-instead-of-a-controlled-script.md
    # for why that was wrong) - backfilling in place is what actually ships.
    conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT UNIQUE NOT NULL")
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


def backfill_missing_usernames(conn: psycopg.Connection) -> list[tuple[int, str]]:
    """One-time migration companion to ensure_schema()'s username column
    (see the comment above it) - assigns an opaque username (same
    generation as app.accounts.create_account) to any existing row that
    doesn't have one yet, in place, rather than deleting and recreating
    accounts. Safe to call whether or not the column exists yet (adds it
    nullable first) and idempotent - a row that already has a username is
    left untouched. Caller commits; see scripts/backfill_username.py for
    the one-off CLI entry point run once against prod.

    Returns the (user_id, new_username) pairs actually assigned, so a
    caller can print/log exactly what changed.
    """
    conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT")
    rows = conn.execute("SELECT id FROM users WHERE username IS NULL").fetchall()
    assigned = []
    for (user_id,) in rows:
        # Same generation as app.accounts.create_account - 16 bytes / 32
        # hex chars, so a backfilled account's username is indistinguishable
        # from one create_account.py would have generated.
        username = secrets.token_hex(16)
        conn.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        assigned.append((user_id, username))
    conn.execute("ALTER TABLE users ALTER COLUMN username SET NOT NULL")
    conn.execute(
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'users_username_key'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT users_username_key UNIQUE (username);
            END IF;
        END $$;
        """
    )
    return assigned
