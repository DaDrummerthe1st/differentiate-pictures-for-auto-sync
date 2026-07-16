import psycopg
import pytest

from app.accounts import create_account
from app.security import verify_password


def test_create_account_inserts_a_row(db_connection):
    user_id = create_account(
        db_connection,
        email="new-member@example.test",
        password="correct horse battery staple",
        role="member",
    )

    row = db_connection.execute(
        "SELECT id, email, password_hash, role FROM users WHERE email = %s",
        ("new-member@example.test",),
    ).fetchone()

    assert row == (user_id, "new-member@example.test", row[2], "member")
    assert verify_password("correct horse battery staple", row[2]) is True


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
