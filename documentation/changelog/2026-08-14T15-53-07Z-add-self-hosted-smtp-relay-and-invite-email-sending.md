# Add self-hosted SMTP relay and invite-email sending

Added a self-hosted boky/postfix relay (digest-pinned, no versioned tag published upstream) to docker-compose.prod.yml plus app/mail.py's best-effort send_invite_email - self-hosted rather than a third-party API since POLICY.md forbids sending invitee emails to a cloud API. DEPLOYMENT.md documents the DKIM/SPF/DMARC DNS steps needed for real deliverability. Not yet wired into the invite route - the accept-invite link needs the frontend page (next step) to exist first.

- **Doc size**: DEPLOYMENT.md +2219 chars.
