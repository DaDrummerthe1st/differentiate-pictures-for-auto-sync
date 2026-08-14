import psycopg
import pytest

from app.db import backfill_missing_usernames, ensure_schema


def test_backfill_assigns_an_opaque_username_to_a_row_missing_the_column(db_connection):
    # Simulates prod's actual 2026-08-13 state: username predates the
    # column entirely (not a NULL value in an existing column).
    db_connection.execute("ALTER TABLE users DROP COLUMN username")
    db_connection.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        ("legacy@example.test", "placeholder-hash-value", "member"),
    )

    assigned = backfill_missing_usernames(db_connection)

    assert len(assigned) == 1
    user_id, username = assigned[0]
    assert len(username) == 32
    int(username, 16)  # raises ValueError if it isn't real hex

    row = db_connection.execute("SELECT username FROM users WHERE id = %s", (user_id,)).fetchone()
    assert row == (username,)


def test_backfill_gives_distinct_usernames_to_multiple_legacy_rows(db_connection):
    db_connection.execute("ALTER TABLE users DROP COLUMN username")
    db_connection.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s), (%s, %s, %s)",
        (
            "legacy1@example.test", "placeholder-hash-value", "member",
            "legacy2@example.test", "placeholder-hash-value", "admin",
        ),
    )

    assigned = backfill_missing_usernames(db_connection)

    usernames = [username for _, username in assigned]
    assert len(usernames) == 2
    assert len(set(usernames)) == 2


def test_backfill_is_a_no_op_once_every_row_already_has_a_username(db_connection):
    db_connection.execute(
        "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
        ("already-set@example.test", "already-set-token", "placeholder-hash-value", "member"),
    )

    assigned = backfill_missing_usernames(db_connection)

    assert assigned == []


def test_username_stays_unique_after_backfill(db_connection):
    db_connection.execute("ALTER TABLE users DROP COLUMN username")
    db_connection.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        ("legacy@example.test", "placeholder-hash-value", "member"),
    )
    (_, existing_username), = backfill_missing_usernames(db_connection)

    with pytest.raises(psycopg.errors.UniqueViolation):
        db_connection.execute(
            "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            ("second@example.test", existing_username, "placeholder-hash-value", "member"),
        )


def test_ensure_schema_succeeds_after_backfill_against_prod_shaped_data(db_connection):
    # This is the actual crash-loop repro: ensure_schema()'s own
    # ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT UNIQUE NOT
    # NULL fails outright against a non-empty table with no username
    # column yet. backfill_missing_usernames() must leave the table in a
    # state where a subsequent ensure_schema() call (i.e. auth's next
    # startup) no longer raises.
    db_connection.execute("ALTER TABLE users DROP COLUMN username")
    db_connection.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        ("legacy@example.test", "placeholder-hash-value", "member"),
    )

    backfill_missing_usernames(db_connection)
    ensure_schema(db_connection)  # must not raise
