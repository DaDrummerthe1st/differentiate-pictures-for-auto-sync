def test_login_page_serves_html_form(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")
    body = res.text
    assert '<form' in body
    assert 'type="email"' in body
    assert 'type="password"' in body
    assert "/login" in body  # the form POSTs to the login API


def test_login_page_response_has_no_server_stack_leak(client):
    res = client.get("/login")
    assert "server" not in res.headers or "uvicorn" not in res.headers["server"].lower()
