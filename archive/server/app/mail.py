import os
import smtplib
from email.message import EmailMessage


def _smtp_config() -> dict[str, object] | None:
    # SMTP is optional, unlike REQUIRED_AUTH_ENV_VARS in app/config.py - no
    # local/dev/test environment runs the self-hosted relay (docker-
    # compose.prod.yml's "smtp" service), so a send is always best-effort:
    # an invite is still fully usable via the token/link the API response
    # already returns directly, even if this returns None or send_invite_email
    # below fails.
    host = os.environ.get("SMTP_HOST")
    if not host:
        return None
    return {
        "host": host,
        "port": int(os.environ.get("SMTP_PORT", "25")),
        "from_addr": os.environ.get("SMTP_FROM", "noreply@localhost"),
    }


def send_invite_email(to_email: str, accept_url: str) -> bool:
    """Best-effort - never raises. Returns whether a send was attempted
    and actually succeeded, purely so a caller can log/audit it; invite
    creation itself must never fail just because mail delivery did (see
    _smtp_config's docstring)."""
    config = _smtp_config()
    if config is None:
        return False

    message = EmailMessage()
    message["Subject"] = "You've been invited"
    message["From"] = config["from_addr"]
    message["To"] = to_email
    message.set_content(f"You've been invited. Use this link to accept:\n\n{accept_url}")

    try:
        with smtplib.SMTP(config["host"], config["port"], timeout=10) as smtp:
            smtp.send_message(message)
    except OSError:
        return False
    return True
