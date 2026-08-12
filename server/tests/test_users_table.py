import psycopg
import pytest


def test_insert_and_read_round_trip(db_connection):
    db_connection.execute(
        "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
        ("member@example.test", "member-token", "placeholder-hash-value", "member"),
    )

    row = db_connection.execute(
        "SELECT email, username, password_hash, role FROM users WHERE email = %s",
        ("member@example.test",),
    ).fetchone()

    assert row == ("member@example.test", "member-token", "placeholder-hash-value", "member")


def test_email_must_be_unique(db_connection):
    db_connection.execute(
        "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
        ("dup@example.test", "dup-token-1", "placeholder-hash-value", "member"),
    )

    with pytest.raises(psycopg.errors.UniqueViolation):
        db_connection.execute(
            "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            ("dup@example.test", "dup-token-2", "placeholder-hash-value", "member"),
        )


def test_username_must_be_unique(db_connection):
    db_connection.execute(
        "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
        ("first@example.test", "dup-username", "placeholder-hash-value", "member"),
    )

    with pytest.raises(psycopg.errors.UniqueViolation):
        db_connection.execute(
            "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            ("second@example.test", "dup-username", "placeholder-hash-value", "member"),
        )
