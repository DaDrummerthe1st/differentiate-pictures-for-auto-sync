import psycopg
import pytest

from app.accounts import create_account
from app.security import verify_password


def test_create_account_inserts_a_row(db_connection):
    user_id, username = create_account(
        db_connection,
        email="new-member@example.test",
        password="correct horse battery staple",
        role="member",
    )

    row = db_connection.execute(
        "SELECT id, email, username, password_hash, role FROM users WHERE email = %s",
        ("new-member@example.test",),
    ).fetchone()

    assert row == (user_id, "new-member@example.test", username, row[3], "member")
    assert verify_password("correct horse battery staple", row[3]) is True


def test_create_account_generates_an_opaque_username(db_connection):
    # Random, not derived from email/role - see documentation/GLOSSARY.md's
    # "Opaque token" entry: used for dpfas_media/<username>/ folder scoping,
    # must not be guessable or human-chosen.
    _, first = create_account(
        db_connection,
        email="opaque-one@example.test",
        password="correct horse battery staple",
        role="member",
    )
    _, second = create_account(
        db_connection,
        email="opaque-two@example.test",
        password="correct horse battery staple",
        role="member",
    )

    assert first != second
    int(first, 16)  # raises ValueError if it isn't real hex
    assert len(first) == 32


def test_create_account_defaults_invites_remaining_to_zero(db_connection):
    create_account(
        db_connection,
        email="no-quota@example.test",
        password="correct horse battery staple",
        role="member",
    )

    row = db_connection.execute(
        "SELECT invites_remaining FROM users WHERE email = %s", ("no-quota@example.test",)
    ).fetchone()

    assert row == (0,)


def test_create_account_accepts_an_explicit_invites_remaining(db_connection):
    create_account(
        db_connection,
        email="has-quota@example.test",
        password="correct horse battery staple",
        role="member",
        invites_remaining=3,
    )

    row = db_connection.execute(
        "SELECT invites_remaining FROM users WHERE email = %s", ("has-quota@example.test",)
    ).fetchone()

    assert row == (3,)


def test_create_account_rejects_duplicate_email(db_connection):
    create_account(
        db_connection,
        email="dup-account@example.test",
        password="correct horse battery staple",
        role="member",
    )

    with pytest.raises(psycopg.errors.UniqueViolation):
        create_account(
            db_connection,
            email="dup-account@example.test",
            password="a different password",
            role="admin",
        )
