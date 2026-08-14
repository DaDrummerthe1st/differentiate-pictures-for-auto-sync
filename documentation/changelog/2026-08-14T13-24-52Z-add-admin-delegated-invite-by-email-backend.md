# Add admin-delegated invite-by-email backend

Lets any account create pending invites (POST /invites) and an invitee accept one to self-create a member account (POST /invites/{token}/accept), instead of every account needing an admin-run CLI command. Delegation is admin-gated via users.invites_remaining. Link-only for now - real email sending is a separate follow-up piece.

- **Doc size**: GLOSSARY.md +616, AUTHENTICATION.md +1632 chars.
