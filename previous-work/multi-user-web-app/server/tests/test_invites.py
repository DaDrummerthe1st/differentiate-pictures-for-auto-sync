from datetime import datetime, timedelta, timezone

from app.accounts import create_account
from app.invites import accept_invite, create_invite, get_invite_by_token
from app.security import verify_password


def _seed_inviter(db_connection, email="inviter@example.test", role="admin"):
    user_id, _ = create_account(
        db_connection, email=email, password="correct horse battery staple", role=role
    )
    return user_id


def test_create_invite_inserts_a_pending_row(db_connection):
    inviter_id = _seed_inviter(db_connection)

    invite = create_invite(db_connection, inviter_id=inviter_id, invitee_email="invitee@example.test")

    assert invite.invitee_email == "invitee@example.test"
    assert invite.inviter_id == inviter_id
    assert invite.status == "pending"
    assert invite.granted_invites == 0
    assert invite.accepted_user_id is None


def test_create_invite_generates_an_unguessable_token(db_connection):
    inviter_id = _seed_inviter(db_connection)

    first = create_invite(db_connection, inviter_id=inviter_id, invitee_email="one@example.test")
    second = create_invite(db_connection, inviter_id=inviter_id, invitee_email="two@example.test")

    assert first.token != second.token
    assert len(first.token) >= 16


def test_create_invite_expires_seven_days_out(db_connection):
    inviter_id = _seed_inviter(db_connection)
    now = datetime(2026, 8, 14, tzinfo=timezone.utc)

    invite = create_invite(
        db_connection, inviter_id=inviter_id, invitee_email="expiry@example.test", now=now
    )

    assert invite.expires_at == now + timedelta(days=7)


def test_get_invite_by_token_round_trips(db_connection):
    inviter_id = _seed_inviter(db_connection)
    created = create_invite(db_connection, inviter_id=inviter_id, invitee_email="lookup@example.test")

    found = get_invite_by_token(db_connection, created.token)

    assert found == created


def test_get_invite_by_token_returns_none_for_unknown_token(db_connection):
    assert get_invite_by_token(db_connection, "not-a-real-token") is None


def test_accept_invite_creates_a_member_account_regardless_of_inviters_role(db_connection):
    inviter_id = _seed_inviter(db_connection, role="admin")
    invite = create_invite(
        db_connection, inviter_id=inviter_id, invitee_email="new-member@example.test"
    )

    user_id, username = accept_invite(db_connection, invite=invite, password="a new password")

    row = db_connection.execute(
        "SELECT email, username, role, password_hash FROM users WHERE id = %s", (user_id,)
    ).fetchone()
    assert row[0] == "new-member@example.test"
    assert row[1] == username
    assert row[2] == "member"
    assert verify_password("a new password", row[3]) is True


def test_accept_invite_carries_the_granted_invites_onto_the_new_account(db_connection):
    inviter_id = _seed_inviter(db_connection)
    invite = create_invite(
        db_connection,
        inviter_id=inviter_id,
        invitee_email="delegated@example.test",
        granted_invites=2,
    )

    user_id, _ = accept_invite(db_connection, invite=invite, password="a new password")

    row = db_connection.execute(
        "SELECT invites_remaining FROM users WHERE id = %s", (user_id,)
    ).fetchone()
    assert row == (2,)


def test_accept_invite_marks_the_invite_accepted(db_connection):
    inviter_id = _seed_inviter(db_connection)
    invite = create_invite(
        db_connection, inviter_id=inviter_id, invitee_email="marks-accepted@example.test"
    )

    user_id, _ = accept_invite(db_connection, invite=invite, password="a new password")

    updated = get_invite_by_token(db_connection, invite.token)
    assert updated.status == "accepted"
    assert updated.accepted_user_id == user_id
