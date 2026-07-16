# TODO

## Next phase: login/authentication

Currently no-login by design (LAN-only, single-household, one-off use
case). Before this app is used by multiple people or leaves the LAN,
add a proper login layer. Requirements as given:

- **Passkeys** as the primary login method (WebAuthn), not just
  password-based auth.
- **Session hijacking protection**: secure, httpOnly, SameSite cookies
  for session tokens; rotate session identifiers on login; consider
  binding sessions to IP/user-agent fingerprint with re-auth on
  mismatch.
- **Real TLS**, not the current self-signed cert (e.g. via a reverse
  proxy with a proper certificate, or a local CA the household trusts) -
  needed once this isn't purely LAN-local.
- **Password length requirement only** - no composition rules (no
  forced mix of uppercase/digits/symbols). This matches current
  NIST guidance and avoids pushing users toward predictable patterns.
- **Reject known-breached passwords** (e.g. check against
  Have I Been Pwned's range API or an equivalent offline breached-
  password list) so a legitimate user isn't tempted to reuse an old,
  already-leaked password just because it's convenient - the login
  flow needs to stay easy enough (passkeys, password manager-friendly)
  that reuse is never the path of least resistance.
- **Per-user isolation of PII**: each user should only ever see their
  own photos/stories/voiceovers once multi-user support exists, not a
  shared pool.

Not started - no code, no design doc yet. Flagged by Joakim on
2026-07-16 as the deliberate next step after the current no-login
single-user version is done.

## Other open items (carried over, not yet done)

- Delete stray leftover zip files sitting in old zipcache docker
  volumes (pre-existing debris from before the caching fix).
- Write documentation describing this app generically (no
  personal/family references) if it's ever shared/open-sourced.
- Recheck for anything else possibly missing from the branch-mixup
  incident earlier in this project's history.
