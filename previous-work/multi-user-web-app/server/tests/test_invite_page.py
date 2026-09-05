def test_accept_invite_page_serves_html_form(client):
    res = client.get("/accept-invite")

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")
    body = res.text
    assert "<form" in body
    assert 'type="password"' in body
    # The token comes from the URL's own query string, read client-side
    # (URLSearchParams) rather than the server reflecting an
    # attacker-controlled query param back into rendered HTML - same
    # reasoning as login_page.py's fully-static HTML with no server-side
    # interpolation of request data at all.
    assert "URLSearchParams" in body
    assert "/invites/" in body and "/accept" in body


def test_accept_invite_page_response_has_no_server_stack_leak(client):
    res = client.get("/accept-invite")

    assert "server" not in res.headers or "uvicorn" not in res.headers["server"].lower()
