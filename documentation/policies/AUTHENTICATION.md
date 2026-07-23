# Authentication & session security

Current state, decisions, and priority order for login/session security across both `app/` (photo-viewer) and `server/` (auth backend) — the project-wide authoritative source for this topic, consolidated 2026-07-23 from requirements that used to live only in [../gui/TODO.md](../gui/TODO.md). This file covers *authentication* (who can log in, how a session is trusted) and session-level security; per-resource *authorization* (who can see/edit which photo, once multi-user upload/sharing exists) is a separate, not-yet-designed concern — see [../gui/TODO.md](../gui/TODO.md)'s multi-user features note.

## Current state (done, live in production since 2026-07-17)

- Password hashing: argon2id (`argon2-cffi`), OWASP's current recommendation over bcrypt.
- Sessions: JWT access (5 min TTL) + refresh (12h TTL) tokens, Redis-backed for revocation. Cookies are `httpOnly`, `Secure`, `SameSite=Strict`.
- Rate limiting: `slowapi`, IP-keyed, on `POST /login`.
- `app/` (photo-viewer) does not implement its own auth — every API route verifies the JWT cookie issued by `server/`'s auth backend via a shared `JWT_SECRET_KEY` (`app/auth.py`'s `require_session`), no shared code deployment between the two images.
- Two fixed accounts only, created via `server/scripts/create_account.py`, never a public signup endpoint.
- Full build history/rationale: [../photo-server/TODO.md](../photo-server/TODO.md) Phase 1.

## Decision: no third-party/social OAuth (2026-07-23)

Raised again this session ("if we use OAuth, does local dev need to be secure too?") — resolved by re-surfacing a decision already made 2026-07-16 and recorded in `../photo-server/TODO.md`'s Phase 1 note: **Google OAuth (or any third-party/social sign-in) is explicitly out of scope**, not merely deferred. It calls out to a cloud identity provider, which conflicts with [POLICY.md](POLICY.md)'s closed-by-default rule ("no photo or user data ever leaves the server... no cloud APIs"; the sole existing exception is Let's Encrypt certificate issuance). This isn't a priority call to revisit later — it's excluded by an existing hard constraint. Continue with the already-built preset-account + password (argon2id) + JWT flow.

This also answers why local dev never needed anything resembling OAuth-grade infrastructure: the local stack ([../gui/README.md](../gui/README.md)) intentionally uses the *same* preset-account/password + JWT flow as production, just with fixed non-secret dev credentials — there's no separate "local needs to be secure for OAuth" concern, because OAuth was never the direction.

Passkeys/WebAuthn (below) are **not** the same category — they're a W3C standard verified locally against public keys the app itself stores (no third-party relying-party service), so they stay inside the closed-by-default posture. A self-hosted OAuth/OIDC *server* (as opposed to a third-party one) would technically also be closed-by-default-compatible, but isn't currently planned or needed at two-account family scale.

## Priority order for remaining hardening

Requirements as originally given by Joakim (2026-07-16), none built yet beyond the base layer above. Ordered by what closes the biggest real gap first, not by how the list was originally written:

1. **Reject known-breached passwords** — the base layer has no blocklist check yet, and this is the one item current external guidance (below) actively requires, not just recommends. Prefer a **self-hosted** breached-password corpus (e.g. [IncogniPwn](https://github.com/millaguie/IncogniPwn) or [Have I Been Pwned's own offline Pwned Passwords downloader](https://haveibeenpwned.com/Passwords)) over calling the live `haveibeenpwned.com` k-anonymity API — the live API only ever receives a 5-character SHA-1 hash prefix of the password (never the password itself, confirmed via [Troy Hunt's k-anonymity writeup](https://www.troyhunt.com/understanding-have-i-been-pwneds-use-of-sha-1-and-k-anonymity/)), but self-hosting keeps this fully inside POLICY.md's closed-by-default posture rather than relying on "the prefix alone isn't sensitive" as a judgment call.
2. **Session-hijacking hardening on top of the already-`Secure`/`httpOnly`/`SameSite=Strict` cookies**: rotate session identifiers on login; consider binding sessions to an IP/user-agent fingerprint with re-auth on mismatch. Not started.
3. **Passkeys (WebAuthn) as an additional login method.** [OWASP's Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) treats passkeys as the current industry direction, to be evaluated before further password-only investment — but per the decision above, this augments the existing password+JWT flow rather than replacing it outright, and needs no third-party relying-party service.
4. **Password policy: length requirement only, no composition rules.** Confirmed current authority is [NIST SP 800-63-4](https://pages.nist.gov/800-63-3/sp800-63b.html) (Revision 4, effective 2025-08-01, supersedes 800-63B): minimum 15 characters when a password is the only login factor (8 with MFA/passkey present), composition rules (forced uppercase/digit/symbol mixes) explicitly prohibited rather than just discouraged, and systems should accept passwords up to 64+ characters, spaces, and paste. Not yet enforced in `server/app/security.py` — currently no minimum-length check at all.
5. **Per-user isolation of PII** (each user sees only their own photos/stories/voiceovers) — genuinely a multi-user *authorization* concern, not authentication; tracked with the upload/shared-folder/rename-audit-log feature set in [../gui/TODO.md](../gui/TODO.md), not built here.

## Sources

- [NIST SP 800-63B / 800-63-4](https://pages.nist.gov/800-63-3/sp800-63b.html) — current password-composition and length guidance.
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — passkeys/WebAuthn as current direction.
- [Have I Been Pwned: Pwned Passwords](https://haveibeenpwned.com/Passwords) and [Troy Hunt's k-anonymity explainer](https://www.troyhunt.com/understanding-have-i-been-pwneds-use-of-sha-1-and-k-anonymity/) — breach-password check mechanics.
- [IncogniPwn](https://github.com/millaguie/IncogniPwn) — self-hosted HIBP-compatible option.

Looked up 2026-07-23; logged per `~/.claude/CLAUDE.md`'s research-log rule in `~/.claude/research_log.jsonl` (not part of this repo). Re-check before relying on specifics if this file is read long after that date — guidance in this space moves.
