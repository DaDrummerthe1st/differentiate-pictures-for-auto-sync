from app.accounts import create_account


def test_sixth_login_attempt_in_a_minute_from_same_ip_is_throttled(
    client, db_connection, redis_client
):
    create_account(
        db_connection,
        email="rate-limited@example.test",
        password="correct horse battery staple",
        role="member",
    )

    responses = [
        client.post(
            "/login",
            json={"email": "rate-limited@example.test", "password": "wrong password"},
        )
        for _ in range(6)
    ]

    statuses = [r.status_code for r in responses]
    assert statuses[:5] == [401, 401, 401, 401, 401]
    assert statuses[5] == 429
