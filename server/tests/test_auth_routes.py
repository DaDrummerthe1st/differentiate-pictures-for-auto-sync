from unittest.mock import patch

from app.accounts import create_account
from app.cookies import ACCESS_COOKIE, REFRESH_COOKIE
from app.security import verify_password

_GENERIC_ERROR = "Incorrect email or password"


def _seed_user(db_connection, email="member@example.test", password="correct horse battery staple"):
    create_account(db_connection, email=email, password=password, role="member")


def test_login_with_correct_credentials_sets_cookies_and_returns_200(client, db_connection):
    _seed_user(db_connection)

    response = client.post(
        "/login",
        json={"email": "member@example.test", "password": "correct horse battery staple"},
    )

    assert response.status_code == 200
    assert response.json() == {"email": "member@example.test", "role": "member"}
    assert ACCESS_COOKIE in response.cookies
    assert REFRESH_COOKIE in response.cookies


def test_login_cookies_have_expected_security_flags(client, db_connection):
    _seed_user(db_connection, email="cookieflags@example.test")

    response = client.post(
        "/login",
        json={"email": "cookieflags@example.test", "password": "correct horse battery staple"},
    )

    set_cookie_headers = response.headers.get_list("set-cookie")
    assert len(set_cookie_headers) == 2
    for header in set_cookie_headers:
        lowered = header.lower()
        assert "httponly" in lowered
        assert "secure" in lowered
        assert "samesite=strict" in lowered


def test_login_with_wrong_password_returns_401(client, db_connection):
    _seed_user(db_connection, email="wrongpw@example.test")

    response = client.post(
        "/login", json={"email": "wrongpw@example.test", "password": "not the password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": _GENERIC_ERROR}


def test_login_with_unknown_email_returns_401(client, db_connection):
    response = client.post(
        "/login", json={"email": "no-such-user@example.test", "password": "whatever"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": _GENERIC_ERROR}


def test_login_wrong_password_and_unknown_email_get_identical_response(client, db_connection):
    _seed_user(db_connection, email="wrongpw2@example.test")

    wrong_password_response = client.post(
        "/login", json={"email": "wrongpw2@example.test", "password": "not the password"}
    )
    unknown_email_response = client.post(
        "/login", json={"email": "still-no-such-user@example.test", "password": "whatever"}
    )

    assert wrong_password_response.status_code == unknown_email_response.status_code
    assert wrong_password_response.json() == unknown_email_response.json()


def test_login_always_calls_verify_password_regardless_of_whether_email_exists(
    client, db_connection
):
    _seed_user(db_connection, email="timing@example.test")

    with patch("app.auth_routes.verify_password", wraps=verify_password) as spy:
        client.post("/login", json={"email": "timing@example.test", "password": "wrong"})
        assert spy.call_count == 1

        client.post(
            "/login", json={"email": "no-such-timing-user@example.test", "password": "wrong"}
        )
        assert spy.call_count == 2


def test_protected_route_without_cookie_returns_401(client):
    response = client.get("/whoami")

    assert response.status_code == 401


def test_refresh_with_valid_cookie_rotates_tokens_and_returns_200(client, db_connection):
    _seed_user(db_connection, email="refresh@example.test")
    client.post(
        "/login",
        json={"email": "refresh@example.test", "password": "correct horse battery staple"},
    )
    old_refresh_cookie = client.cookies.get("photo_server_refresh")

    response = client.post("/refresh")

    assert response.status_code == 200
    assert response.json() == {"message": "refreshed"}
    # rotated: the client's cookie jar now holds a different refresh cookie
    assert client.cookies.get("photo_server_refresh") != old_refresh_cookie
    # and the new one actually works for a protected route
    assert client.get("/whoami").status_code == 200


def test_refresh_without_cookie_returns_401(client):
    response = client.post("/refresh")

    assert response.status_code == 401


def test_logout_revokes_refresh_token_and_clears_cookies(client, db_connection):
    _seed_user(db_connection, email="logout@example.test")
    client.post(
        "/login",
        json={"email": "logout@example.test", "password": "correct horse battery staple"},
    )

    logout_response = client.post("/logout")
    refresh_response = client.post("/refresh")

    assert logout_response.status_code == 200
    assert refresh_response.status_code == 401


def test_protected_route_with_valid_access_cookie_returns_200(client, db_connection):
    _seed_user(db_connection, email="whoami@example.test")
    client.post(
        "/login",
        json={"email": "whoami@example.test", "password": "correct horse battery staple"},
    )

    # the client's own cookie jar already carries the cookies login just set
    response = client.get("/whoami")

    assert response.status_code == 200
    assert response.json()["email"] == "whoami@example.test"


def test_failed_login_writes_one_audit_log_row(client, db_connection):
    _seed_user(db_connection, email="audit-fail@example.test")

    client.post(
        "/login", json={"email": "audit-fail@example.test", "password": "wrong password"}
    )

    rows = db_connection.execute(
        "SELECT user_id, action, details FROM audit_log WHERE action = 'login_failure'"
    ).fetchall()

    assert len(rows) == 1
    user_id, action, details = rows[0]
    assert action == "login_failure"
    assert details == {"attempted_email": "audit-fail@example.test"}


def test_failed_login_for_unknown_email_writes_null_user_id(client, db_connection):
    client.post(
        "/login", json={"email": "no-such-audit-user@example.test", "password": "whatever"}
    )

    rows = db_connection.execute(
        "SELECT user_id, details FROM audit_log WHERE action = 'login_failure'"
    ).fetchall()

    assert len(rows) == 1
    assert rows[0][0] is None


def test_successful_login_writes_one_audit_log_row(client, db_connection):
    _seed_user(db_connection, email="audit-success@example.test")

    client.post(
        "/login",
        json={"email": "audit-success@example.test", "password": "correct horse battery staple"},
    )

    rows = db_connection.execute(
        "SELECT user_id, action FROM audit_log WHERE action = 'login_success'"
    ).fetchall()

    assert len(rows) == 1
