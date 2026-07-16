import psycopg
import pytest


def test_insert_and_read_round_trip(db_connection):
    db_connection.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        ("member@example.test", "placeholder-hash-value", "member"),
    )

    row = db_connection.execute(
        "SELECT email, password_hash, role FROM users WHERE email = %s",
        ("member@example.test",),
    ).fetchone()

    assert row == ("member@example.test", "placeholder-hash-value", "member")


def test_email_must_be_unique(db_connection):
    db_connection.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        ("dup@example.test", "placeholder-hash-value", "member"),
    )

    with pytest.raises(psycopg.errors.UniqueViolation):
        db_connection.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
            ("dup@example.test", "placeholder-hash-value", "member"),
        )
