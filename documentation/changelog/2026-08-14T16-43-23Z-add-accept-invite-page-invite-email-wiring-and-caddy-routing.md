# Add accept-invite page, invite-email wiring, and Caddy routing

Added GET /accept-invite (static HTML, token read client-side via URLSearchParams - never server-reflected, avoids XSS), wired send_invite_email into POST /invites with an APP_ORIGIN-based link, and fixed Caddyfile/Caddyfile.local to actually route /invites and /accept-invite to auth (previously unreachable through the proxy - unit tests hit FastAPI directly so this gap wasn't caught by them). 89 server tests passing.

- **Doc size**: docker-compose.prod.yml +286 chars (APP_ORIGIN).
