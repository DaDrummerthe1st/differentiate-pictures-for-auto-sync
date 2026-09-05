from unittest.mock import MagicMock, patch

from app.mail import send_invite_email


def test_send_invite_email_is_a_no_op_when_smtp_host_is_not_configured(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)

    with patch("app.mail.smtplib.SMTP") as smtp_cls:
        result = send_invite_email("invitee@example.test", "https://photos.example.test/accept-invite?token=abc")

    assert result is False
    smtp_cls.assert_not_called()


def test_send_invite_email_sends_via_configured_smtp_host(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.internal.test")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("SMTP_FROM", "noreply@photos.example.test")
    mock_smtp = MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp

    with patch("app.mail.smtplib.SMTP", return_value=mock_smtp) as smtp_cls:
        result = send_invite_email("invitee@example.test", "https://photos.example.test/accept-invite?token=abc")

    assert result is True
    smtp_cls.assert_called_once_with("smtp.internal.test", 25, timeout=10)
    sent_message = mock_smtp.send_message.call_args[0][0]
    assert sent_message["To"] == "invitee@example.test"
    assert sent_message["From"] == "noreply@photos.example.test"
    assert "accept-invite?token=abc" in sent_message.get_content()


def test_send_invite_email_returns_false_on_connection_failure(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.internal.test")

    with patch("app.mail.smtplib.SMTP", side_effect=OSError("connection refused")):
        result = send_invite_email("invitee@example.test", "https://photos.example.test/accept-invite?token=abc")

    assert result is False
