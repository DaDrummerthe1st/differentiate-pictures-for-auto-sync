from app.audit import log_audit_event


def test_log_audit_event_inserts_a_row(db_connection):
    log_audit_event(
        db_connection,
        action="login_failure",
        user_id=None,
        details={"attempted_email": "no-such-user@example.test"},
    )

    row = db_connection.execute(
        "SELECT user_id, action, catalogue, filename, details FROM audit_log"
    ).fetchone()

    assert row == (
        None,
        "login_failure",
        None,
        None,
        {"attempted_email": "no-such-user@example.test"},
    )
