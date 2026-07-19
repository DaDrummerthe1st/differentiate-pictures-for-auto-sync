# TODO — photo-server

## How to use this roadmap

- One numbered step per session — each is sized to TDD in a single
  sitting: a failing test, minimal code to pass it, output shown, full
  suite green, commit.
- Steps are in dependency order. Don't skip ahead — later steps assume
  earlier ones are done and tested.
- Every step has a **Security** line. Don't skip it even when the step
  looks purely functional — that's how gaps get missed.
- **(human checkpoint)** steps need Joakim to run something manually
  before the next step starts.
- Login (Phases 0–1) is priority one, ahead of every other phase,
  including ahead of the rest of the original schema. Nothing in Phase 2
  onward starts until Phase 1 is checkpointed.
- **Every phase that produces user-facing behavior gets an explicit
  frontend step, paired with its backend step(s)** — not left implicit
  or assumed to happen "later." Decided 2026-07-16 after Phase 1 turned
  out to be API-only with no step that actually built the login page,
  unlike Phase 4.6 which does build the thumbnail screen. Checked
  retroactively against every phase below; 4.8/4.9 were the other gaps
  found.
- **A GUI-facing step isn't build-ready until its spec clears the same
  bar as MOCKUP.md's Login screen section**: every field/element present
  (and what's explicitly absent), every state enumerated with exact
  user-facing wording where applicable, the transition for each state,
  which backend endpoint(s) it calls, and an explicit list of what's
  deferred and to where. A step that only *names* a screen ("lightbox",
  "search panel") without that detail is not well-defined — write or
  request the actual spec before starting, don't invent UX decisions to
  fill the gap. 4.8 and 4.9 are marked **(blocked on spec)** for exactly
  this reason.
- **Every phase with user-facing behavior ends with a human checkpoint
  that includes deliberate misuse, not just the happy path** — "if the
  user can do wrong, the user will do wrong" (empty/whitespace-only
  fields, absurdly long input, double-submitting a form, the browser
  back button after logout, a narrow window width). This requires that
  phase's GUI step(s) to actually be built by then, not just its API —
  a human clicking through the real screen is also how layout bugs
  (overflowing text boxes, wrapping, truncation) get caught; `curl`
  can't reveal those. Decided 2026-07-16. Audited every phase below:
  Phase 4 had no human checkpoint at all (added one); Phase 1's 1.11 and
  Phase 5's existing checkpoint had their wording strengthened past
  happy-path only; Phase 2 has none by design (schema only, no
  user-facing behavior — see its own note) rather than by oversight.

**Before Phase 1 starts**: confirm whether Joakim's existing login
implementation (from another project) replaces the spec below or is
adapted into it. Phase 1 as written is a fallback spec, not a locked-in
design.

## Branch relationship — read before merging anything

Three branches carry this project's history, and they are **not** a
normal linear feature-branch chain:

- `master` — this repo's mainline. Has `server/app/{config,db,main}.py`
  only; no auth code at all (`server/app/main.py` here is just a bare
  `/health` route).
- `phase-1-login` — `master` + 24 commits building the full auth backend
  (`accounts.py`, `audit.py`, `auth_routes.py`, `cookies.py`,
  `rate_limit.py`, `security.py`, `tokens.py`, this file's Phase 0/1).
  Normal history: `master` is a real ancestor (0 commits in `master` are
  missing from `phase-1-login`).
- `mamma-photo-viewer` — the GUI photo-viewer app (`app/`), built as a
  **quick, deliberately disposable copy of another repo**, committed as
  a fresh **orphan branch** (root commit "Initial empty commit",
  2026-07-16) with **no shared git history with `master` at all**
  (`git merge-base mamma-photo-viewer master` returns nothing). Despite
  that, its `server/app/` tree already contains the exact same 7 auth
  files as `phase-1-login` — byte-identical, confirmed via diff
  2026-07-17 — because the branch was seeded from a `phase-1-login`
  snapshot rather than from `master`. A plain `git merge master` here
  hits `fatal: refusing to merge unrelated histories`; forcing it with
  `--allow-unrelated-histories` produces **24 real file conflicts**
  (`CLAUDE.md`, `README.md`, `CHANGELOG.md`, both `main.py`'s,
  `server/pyproject.toml` + `server/uv.lock`, `server/docker-compose.yml`,
  the append-only `tools/*/*.jsonl` logs, several `documentation/
  photo-server/*.md` files) — checked 2026-07-17, not yet resolved.

**Decision (2026-07-17, mid-deadline session)**: do not merge today.
`mamma-photo-viewer` already has everything P0 needs (the auth backend
files), so a merge buys nothing for that deadline and only costs time on
conflict resolution. The P0 session instead ported the *wiring*
(`app/auth.py`, the login page, Caddy config) directly onto
`mamma-photo-viewer`, no git merge involved.

**P1, no deadline pressure**: Joakim wants history preserved, not
squashed or cherry-picked away — the end state is everything folded into
one surviving `master`, by an actual `git merge --allow-unrelated-
histories` (or equivalent), resolving the 24 conflicts above carefully,
not a shortcut that drops attribution. `phase-1-login` should fold in
first (clean ancestry with `master`, zero conflicts) or can be treated as
already-superseded once `mamma-photo-viewer`'s auth files are confirmed
identical and current. Do this once, calmly, with no clock running.

## Phase 0 — Minimal scaffold (only what auth needs, nothing more)

0.1 `GET /health` returns `{"status":"ok"}`, 200. Write the test failing
first (pytest + FastAPI's `TestClient`), then the minimal FastAPI route
to pass it. **Security**: response leaks no version/stack info.

0.2 Dockerfile (slim base) + docker-compose.yml with two services: `app`
(bound to 127.0.0.1 only, explicit `mem_limit`) and `postgres` (official
image, explicit `mem_limit`, named volume, conservative
`max_connections`/`shared_buffers`). Compose smoke test: build the
image, curl `/health` via the `app` container's published port
(`127.0.0.1:8000`, from the host — not `docker exec` into the
container). **Security**: no ports
published except through the app service; no default/blank Postgres
password — generated and passed via env var, never hardcoded. Also carried
over from 0.1: uvicorn's default `Server: uvicorn` response header leaks
the stack — the Dockerfile `CMD`/compose command must launch uvicorn with
`server_header=False` (confirmed via `uv run uvicorn app.main:app` + curl
against 0.1's route that the default leaks this; TestClient can't catch
it since it bypasses the real transport). **Before running `compose up`
on the target host, check [HARDWARE.md](HARDWARE.md)'s memtest gate —
it may not be cleared yet; build/test images on a dev machine until it
is.** (human checkpoint: run the smoke test yourself, confirm the curl
response.)

0.3 `users` table only (id, email, password_hash, role, created_at) —
nothing else from the full schema yet. Test: round-trip insert/read,
`unique(email)`. **Security**: `password_hash` column never appears in
any log statement or test assertion output in plaintext-adjacent form.

0.4 (done) All paths and DB connection details from environment
variables only — test that a missing required env var fails startup
immediately (fail-fast) rather than falling back to a default.
`app/config.py`'s `load_db_config()` reads the five `POSTGRES_*` vars
with no defaults and raises `MissingConfigError` if any are absent;
`app/main.py` calls it at module import time, so a bare `uvicorn
app.main:app` refuses to start before binding a port if config is
missing, rather than failing lazily on the first DB-touching request.
`docker-compose.yml`'s `app` service now passes the five vars through
explicitly (previously it defined none, which — with this fail-fast
check now in place — would have kept `docker compose up`'s app
container from starting at all). **Security**: confirmed `.env` is
gitignored (it already was, pre-dating this step).

## Phase 1 — Complete login system (priority one)

**Architecture, decided 2026-07-16 (superseding the fallback spec this
phase originally had):** Joakim's existing login implementation, in
`../../project/buzzkit` (sibling repo, not part of this one), is ported
in and adapted rather than building the original bcrypt/DB-session
fallback from scratch. Two deliberate deviations from buzzkit's code,
confirmed with Joakim rather than assumed:
- **Password hashing is argon2id** (`argon2-cffi`'s `PasswordHasher`,
  ported from buzzkit's `app/core/security.py`), not bcrypt as this
  spec originally said — argon2id is OWASP's current recommendation for
  new applications over bcrypt. `password_hash` in
  [DATA_DICTIONARY.md](DATA_DICTIONARY.md) is now labelled `argon2id`,
  not `bcrypt`.
- **Sessions are JWT access + refresh tokens, Redis-backed for
  revocation** (ported from buzzkit's `app/core/security.py` +
  `app/core/cookies.py`), not the plain Postgres-only session-cookie
  design this spec originally sketched. This adds a `redis` service to
  `server/docker-compose.yml` — mem-capped (128m), no host port
  published (internal-only, same pattern as `postgres`), `requirepass`
  via `REDIS_PASSWORD` env var, and **`restart: "no"`** (buzzkit's own
  compose file uses `unless-stopped` on `redis` — deliberately not
  carried over; see this file's Docker rule). Refresh-token TTL is 12h
  here (not buzzkit's 30 days) to preserve this spec's original "session
  expires after 12h" intent for a small, private, two-account server;
  access-token TTL is short (5 min) so a stolen access-token cookie
  alone doesn't grant the full 12h.
- **Rate limiting is `slowapi` + the same Redis instance**, IP-keyed
  (ported from buzzkit's `app/core/rate_limit.py` near-verbatim) — this
  alone satisfies 1.8 below, so buzzkit's separate username-keyed
  `lockout.py` (a 15-minute account lockout, a different mechanism this
  spec never asked for) is not ported.
- `audit_log` (defined in [DATA_DICTIONARY.md](DATA_DICTIONARY.md) under
  Phase 2) is created now, in this phase, since 1.7 needs it — only that
  one table is pulled forward, not the rest of Phase 2's schema.
- Login identifier stays **email**, matching the `users` table already
  built in 0.3 (buzzkit's own login uses `username`; not applicable
  here).

**Explicitly not ported from buzzkit** (out of scope for this project):
the `/signup` endpoint (only the two fixed accounts from 1.2's CLI
exist, ever), Google OAuth (calls out to a cloud API — against this
folder's "no cloud APIs" non-negotiable), analytics/activity-event
emission, the honeypot signup field, and per-request Postgres
row-level-security role switching (this project stays on the single
`photo_server` DB role built in Phase 0). Buzzkit's least-privilege
`security_writer` DB role for its audit table is a real hardening idea
worth revisiting later (see [DEFERRED.md](DEFERRED.md)) but not built
now — a single DB role stays proportionate at two-user scale.

New dependencies (`server/pyproject.toml`): `argon2-cffi`, `pyjwt`,
`redis`, `slowapi` — added as `>=`-only (no upper bound, matching this
project's existing pins), resolved to latest via `uv lock`, and
`pip-audit`-checked clean before use (2026-07-16).

1.1 (done) Password hashing helper: hash + verify round-trip test, using
argon2id (`argon2-cffi`'s `PasswordHasher`, ported from buzzkit's
`hash_password`/`verify_password`/`needs_rehash`, now `server/app/
security.py`). **Security**: confirmed `PasswordHasher()`'s default
variant is actually argon2id, not assumed — `test_hash_uses_argon2id_
variant` asserts the `$argon2id$` prefix on a real produced hash.

1.2 (done) CLI (`server/scripts/create_account.py`, core logic in
`app/accounts.py`) creates the two accounts —
joakim.reuterborg@gmail.com (admin), elisabeth.reuterborg@gmail.com
(member) — argon2id-hashed, password supplied interactively (non-echoed
prompt) or via `CREATE_ACCOUNT_PASSWORD` env var, never as a CLI
argument (would leak into shell history/process listings) or hardcoded
in the repo. Run as `uv run python -m scripts.create_account --email
... --role ...` from `server/` (`scripts/` is a package so `app`
resolves). Test: `app/accounts.py`'s `create_account` inserts a row and
rejects a duplicate email; also hand-smoke-tested the actual CLI
end-to-end against the disposable test container, which caught a
real invocation bug (running the script directly, `python
scripts/create_account.py`, doesn't put `server/` on `sys.path`, so
`app` wasn't importable) — fixed by adding `scripts/__init__.py` and
switching to `-m` invocation.

1.3 (done) `POST /login` with correct email+password → sets access +
refresh JWT cookies (`app/auth_routes.py`, cookies via `app/cookies.py`
— ported from buzzkit's `set_auth_cookies`, renamed off the `buzzkit_*`
cookie names to `photo_server_access`/`photo_server_refresh`), 200.

1.4 (done) `POST /login` with wrong password → 401. Same status/body
for "wrong password" and "unknown email" (`_GENERIC_LOGIN_ERROR`,
ported from buzzkit) — explicit test asserts identical status+body for
both. **Timing found and fixed, not just assumed**: buzzkit's own login
route short-circuits (`auth_row is None or not verify_password(...)`),
so an unknown email never pays argon2's verify cost and returns
measurably faster than a wrong-password attempt — a real timing side
channel, not ported. `app/auth_routes.py` instead always calls
`verify_password` (against a precomputed dummy hash when no user
exists), and `test_login_always_calls_verify_password_regardless_of_
whether_email_exists` asserts the call happens exactly once either way.

1.5 (done) Unauthenticated request to a protected route → 401. Valid
access-token cookie → allowed through — `get_current_user` dependency
in `app/auth_routes.py` (ported from buzzkit's dependency, adapted to
raw psycopg instead of SQLAlchemy), exercised via a new `GET /whoami`
route.

1.6 (done) Refresh token expires after 12h, access token after 5 min —
already tested in the token-layer prerequisite commit
(`tests/test_tokens.py`), via a backdated `now` parameter passed to
token creation rather than a real sleep or a separate mocked-clock
library — same effect (deterministic, no wall-clock dependency),
smaller mechanism.

1.7 (done) Failed logins are written to `audit_log` (table created now
in `app/db.py`'s `ensure_schema`, pulled forward from Phase 2 — see
architecture note above; buzzkit's `log_security_event` ported and
simplified to `app/audit.py`'s `log_audit_event`, single existing DB
role, no separate `security_writer` role yet). Also logs
`login_success` — DATA_DICTIONARY.md's audit_log description already
said "login... actions are logged" without qualifying "failed only", so
this reconciles the literal TODO wording with the broader schema intent
rather than picking one silently. **Real bug found and fixed while
wiring this in**: `app/db.py`'s `get_db()` auto-committed only after a
route returned cleanly; since FastAPI throws a raised `HTTPException`
into the dependency generator at its `yield` point, the failed-login
path never reached that commit line, so the very audit row this step
exists to write would have been silently dropped in the real deployed
app (test coverage didn't catch it either, because the test override
shares the test's own already-open transaction and doesn't need a
commit to see its own writes). Fixed by removing the auto-commit and
committing explicitly at each route's actual write points instead —
same convention `scripts/create_account.py` already used. Test: one
failed login → one row with correct `action`/`details`; one successful
login → one `login_success` row.

1.8 (done) 6th failed attempt within a minute from the same IP → 429,
via `slowapi`'s Redis-backed limiter on `POST /login` (`"5/minute"`,
ported from buzzkit's `app/core/rate_limit.py`, new `app/rate_limit.py`
+ registration in `app/main.py`). Test drives 6 requests, asserts the
first 5 are `401` (wrong password) and the 6th is `429`. Test isolation
note: the limiter's Redis keys on client IP, and `TestClient` always
reports the same fixed address, so the shared `client` test fixture now
also flushes Redis before/after every test (via the existing
`redis_client` fixture) — otherwise one test's login attempts would
count toward the next test's limit.

1.9 **Security pass — gaps not in the original spec, add before calling
Phase 1 done:**
 - (done) Cookie flags: `HttpOnly`, `Secure`, `SameSite=Strict` on both
   the access and refresh cookies — already set in `app/cookies.py` since
   1.3; this step just closed the test-coverage gap
   (`test_login_cookies_have_expected_security_flags` asserts all three
   flags on both `Set-Cookie` headers, not just that login works).
 - (done) **CSRF, confirmed not assumed**: `SameSite=Strict` blocks the
   cookie from being sent on *any* cross-site request, including a
   top-level navigation from another origin — strictly stronger than
   `Lax`, which still allows top-level GET navigations through. The one
   real cost of `Strict` is that following an inbound external link
   (an email link, a bookmark opened fresh) into an authenticated page
   won't carry the cookie on that very first request, so the page loads
   logged-out and needs a second load/click. This app has no such
   inbound-link flow — Elisabeth and Joakim open the site directly, not
   via emailed deep links — so that cost is negligible and `Strict` is
   confirmed sufficient, not just assumed adequate.
 - (done) Logout endpoint: **not in the original build plan at all.**
   `POST /logout` (`app/auth_routes.py`) revokes the refresh token
   server-side in Redis (ported from buzzkit's `revoke_refresh_token`)
   — not just clearing the cookie client-side. **Gap found while
   test-driving this**: TODO.md's own wording here already presumed a
   `POST /refresh` endpoint existed ("the old refresh cookie no longer
   authenticates a `/refresh` call") but no step had ever built one —
   without it, the 5-minute access token had no renewal path at all,
   defeating the point of a 12h refresh token. Added `POST /refresh`
   (rotates both tokens, single-use refresh token like buzzkit) alongside
   logout. Tests: refresh rotates and the new cookie still authenticates;
   refresh without a cookie → 401; after logout, the old refresh cookie
   no longer authenticates `/refresh`.
 - (done) `JWT_SECRET_KEY` minimum length check at startup (buzzkit
   validates ≥32 characters in its config — ported the threshold) — folded
   into `app/config.py`'s existing `load_auth_config()` fail-fast pattern
   from 0.4 rather than a new mechanism.
 - Password reset: **scope decided 2026-07-16, replacing the earlier
   "CLI, accepted gap" note** — self-service email-based reset conflicts
   with this project's no-cloud-APIs rule (needs either a self-hosted
   SMTP relay — a system-level install, deferred indefinitely — or a
   third-party email API, which the rule forbids outright). Instead: an
   in-app, admin-only reset that generates a random password server-side
   (see [MOCKUP.md](MOCKUP.md)'s new "Admin password reset screen"
   section for the full spec). Split into 1.9a–1.9c below.

1.9a `require_admin` dependency (`app/auth_routes.py`) — wraps
`get_current_user`, 403 if `role != "admin"`. Test: an admin passes
through; a member gets 403.

1.9b `POST /admin/users/{user_id}/reset-password` — admin-only
(1.9a), generates a cryptographically random password (`secrets`
module, enough entropy that brute-forcing it isn't practical), hashes
it (1.1's `hash_password`), updates `users.password_hash`, returns the
plaintext password **once** in the response body (never logged, never
written to `audit_log.details` — only that a reset happened, per this
file's cross-cutting checklist on raw sensitive payloads). Logs
`action="password_reset"` to `audit_log`. **Known limitation, not
blocking**: doesn't revoke the reset user's existing refresh
tokens/sessions (Redis only indexes refresh tokens by `jti`, not by
`user_id`, so there's no "revoke all of this user's sessions" operation
yet) — a stolen still-live session survives a password reset until it
naturally expires (≤12h). Worth a Redis secondary index by `user_id` if
this ever matters more than it does at two-user scale; noted in
[DEFERRED.md](DEFERRED.md) rather than built now. Test: non-admin → 403;
admin resets another account's password; the new password logs in; the
old password no longer does.

1.9c Admin password reset frontend, per MOCKUP.md's new section above
(account list, confirm dialog, one-time password display). Same
frontend-pairing rule as 1.10/4.8/4.9 — this is GUI-facing, so it gets
its own step rather than being assumed to ride along with 1.9b's API.

1.10 (done, 2026-07-17, on `mamma-photo-viewer` not `phase-1-login` —
see this file's "Branch relationship" note) Login page frontend (per
[MOCKUP.md](MOCKUP.md)'s Login screen spec — email, password, submit; a
generic error message state; a locked-out state, "Too many attempts, try
again in a minute", for the 1.8 429 case) — minimal HTML/JS served by
the app itself, calling `POST /login`, redirecting to the thumbnail
screen's catalogue list (Phase 4) on success. **Gap found and closed
2026-07-16**: every step through 1.9 above built the API only; nothing
in the original Phase 1 plan actually built a page a person could open
in a browser, unlike Phase 4.6 which explicitly builds the thumbnail
screen's frontend. Added here, before the human checkpoint, so that
checkpoint exercises the real screen rather than `curl`. Built as
`server/app/login_page.py` (`GET /login`, inline HTML/JS, no separate
static file) — tests in `server/tests/test_login_page.py`. Paired with
`app/auth.py` in the photo-viewer (`mamma-photo-viewer`'s `app/`,
different codebase from `server/`) gating every photo/thumbnail/
voiceover route on the same session cookie, and `app.js`'s new
`authFetch` wrapper for silent token refresh — see CHANGELOG 2026-07-17.

1.11 (human checkpoint) Log in as both real accounts with real
passwords you set via 1.2's CLI, through the actual login page (not
`curl`); confirm a wrong password truly fails; confirm logout truly
invalidates the refresh token (old cookie can no longer refresh).
**Misuse pass, not just the happy path** (2026-07-16): submit the form
empty and with a whitespace-only email; paste in an absurdly long
password; submit twice in quick succession (double-click); use the
browser back button after logging out and confirm the protected page
doesn't render from cache; try a narrow/mobile-width window and confirm
the email/password fields and error message don't overflow or clip.

**Phase 1 done = login system complete.** Nothing below starts until
this checkpoint passes.

## Phase 2 — Full photo schema

Everything from the original `photos`, `photo_owners`, `share_links`,
`tags`, `audit_log` design in
[DATA_DICTIONARY.md](DATA_DICTIONARY.md) — note `selections` is
dropped, not built (see that file's flagged call). Tests: round-trip
insert/read per table, `unique(catalogue, filename)` on `photos`,
`unique(photo_id, user_id, tag)` on `tags`, full-text search query
against `search_vector` returns expected rows. **Security**: no table
here is queryable without a `user_id`/`photo_owners` join that scopes
results to the caller — write that as an explicit test per table, not
an assumption.

**No human checkpoint in this phase, by design, not oversight**: schema
only, no endpoint and no user-facing behavior yet — nothing for a human
to click through. Exercised indirectly once Phase 3's checkpoint loads
real data into these tables and Phase 4's builds a screen on top of
them.

## Phase 3 — Ingestion

`server/scripts/ingest.py` scans `/tank/momfiles/library/<catalogue>/`,
populates `photos`, never moves or copies files. One sub-step per file
type family:
- 3.1 Common raster (jpg/jpeg/png/tiff/bmp/gif/heic): row + EXIF
  `DateTimeOriginal`/GPS extraction when present (confirm Pillow's
  actual EXIF API against a real file before writing code — don't
  assume the API shape), null when absent, **no mtime fallback** (see
  DATA_DICTIONARY.md).
- 3.2 RAW (cr2/cr3/nef/arw/dng/orf/rw2/raf/pef): hash + size at minimum;
  confirm which library actually reads RAW EXIF/embedded previews
  against a real sample file before considering this done.
- 3.3 Video (mp4/mov/avi/mkv/wmv/mts/m2ts): hash + size at minimum.
- 3.4 Idempotent re-run via `file_hash` — test ingesting the same
  directory twice produces no duplicate rows.
- 3.5 Reject a renamed `.exe` via magic-byte check, not extension —
  explicit adversarial test (rename a binary to `.jpg`, confirm reject).
  **Security**: this is the one step where untrusted file content is
  parsed by third-party libraries (Pillow, RAW readers, ffmpeg later) —
  treat every ingested file as adversarial input, not just malformed
  input. Pin library versions; a malformed EXIF blob is a plausible
  attack surface, not just a malformed-data edge case.

(human checkpoint) Run `exiftool -DateTimeOriginal` on a few real files
from different discs yourself, confirm real dates survived, before
trusting ingested data.

## Phase 4 — Browse, search, and the thumbnail screen

**Not the same system as `mamma-photo-viewer`'s already-deployed
thumbnails** (2026-07-17 note, to prevent confusion): this phase is the
future Postgres-catalog-backed backend (`server/`, schema-dependent,
not yet built beyond Phase 0/1). The `/thumb` route that was actually
debugged and fixed today (mem_limit, a concurrency semaphore,
`Image.draft()` — see [DEFERRED.md](DEFERRED.md) and
`../bugs/reports/2026-07-17-thumbnail-oom-under-load.md`) lives in
`app/main.py`, the simpler,
filesystem-based `mamma-photo-viewer` app that's actually live in
production right now. Don't assume work here also applies there, or
vice versa.

4.1 `GET /catalogues` — alphabetical, with photo counts.

4.2 `GET /catalogues/{name}/photos` — metadata, 404 on unknown
catalogue, explicit `../../etc` path-traversal test → 400.

4.3 `GET /photos/search` — text query + optional catalogue/date-range
filters, uses the tsvector index, matches across all catalogues.

4.4 `GET .../thumbnail` — 300px JPEG cached to disk; RAW via embedded
preview (confirm the library's actual API first); video via an ffmpeg
frame grab. Second request hits the cache — test cache-hit doesn't
re-invoke ffmpeg/Pillow. **Security**: thumbnail cache path is derived
from `photo_id`, never from user-supplied filename directly, to close
off cache-path traversal; ffmpeg is invoked with an argument list, never
a shell string built from the filename, to close off command injection.

4.5 `GET .../full` — authenticated, traversal-rejected (same test shape
as 4.2).

4.6 Implement the bare-minimum thumbnail screen from
[MOCKUP.md](MOCKUP.md): catalogue title + thumbnail grid, calling 4.1/
4.2/4.4. No tap-to-tag yet (Phase 5).

4.7 Browsing itself is never written to `audit_log` (only mark/download/
login are, per DATA_DICTIONARY.md) — explicit test that a browse request
produces zero new audit rows.

4.8 **(blocked on spec)** Lightbox + info panel frontend — tapping a
thumbnail (4.6's placeholder tap target) opens the full-size image
(4.5) in some kind of overlay, with an info panel showing
catalogue/date/GPS/orientation. **Two gaps found 2026-07-16, not just
one**: (1) MOCKUP.md only *names* "lightbox, info panel" without
specifying it — no fields/states/wording/transitions, unlike the Login
screen section's level of detail; (2) the numbered-step gap this
mirrors 1.10's fix for. Closing (2) without closing (1) would mean
building to an under-specified target. **Before this step starts**:
write (or get from Joakim) an actual spec at the Login-screen's bar —
what the info panel shows and in what layout, how the lightbox opens/
closes/navigates between photos (swipe? arrows? both?), what happens
on a RAW/video file 4.5 can't render inline. Don't invent these UX
decisions — ask.

4.9 **(blocked on spec)** Search/filter panel frontend, wired to 4.3's
`GET /photos/search`. Same two-part gap as 4.8: MOCKUP.md names a
"search/filter panel" with no detail on its fields (text box only?
date-range pickers? catalogue picker?), states (empty results, query
still typing/debounced, filters combined how), or layout. **Before this
step starts**: write/get the actual spec, same bar as 4.8.

(human checkpoint) **Added 2026-07-16 — this phase had none.** Browse a
real catalogue through the actual thumbnail screen (not the raw API):
confirm thumbnails load and the grid looks right at a narrow/mobile
window width (text/title wrapping, no overflow). Misuse pass: an empty
catalogue, a catalogue name long enough to test the "wrapped never
truncated" rule (DATA_DICTIONARY.md), rapid repeated taps on the same
thumbnail, browser back/forward through lightbox opens. Once 4.8/4.9's
specs exist and are built: open the lightbox on a RAW or video file
specifically (the case 4.8's spec must define), and run a search with
no results, a single-character query, and a query plus a date-range
filter together.

## Phase 5 — Tags (albums) and download

5.1 `POST /tags` create, `GET /tags` list caller's own `kind='album'`
tags with live count/size (`SUM(photos.file_size)`, no cache table).

5.2 `POST`/`DELETE /tags/{tag}/photos/{photo_id}` — idempotent both
ways, test double-add and double-remove.

5.3 `GET /tags/{tag}/photos` — list.

5.4 One user's tags are invisible to another — explicit cross-user test,
not just an implicit assumption from the auth layer.

5.5 A photo can carry two tags at once without conflict.

5.6 `GET /tags/{tag}/download` — zip stream, default = only
`downloaded_at IS NULL` for that tag, `?full=true` re-zips everything,
both update `downloaded_at`/`download_count` per photo. Repeatable, not
error-on-redownload. **Security**: zip built from a fixed, server-known
file list per photo row — never from a user-supplied path — to close off
zip-slip/path-injection into the archive.

5.7 Wire the thumbnail screen's tap-to-add gesture and top bar (name,
count, size, download button) — the parts MOCKUP.md deferred out of
Phase 4.

(human checkpoint, from GUI_SPEC's original acceptance test) Create two
tags, add the same photo to both, confirm it appears in both; download
one tag fully, add a new photo, download again with default params,
confirm only the new photo is in the second zip. **Misuse pass added
2026-07-16** (this checkpoint was happy-path only): double-tap the same
thumbnail rapidly to add it to a tag twice, remove a tag while a
download is still in progress, an absurdly long tag name, tapping the
download button twice in quick succession, and confirm the top bar
(name/count/size) doesn't overflow or clip at a narrow window width.

## Phase 6 — HTTPS and deployment

**Built early and out of order, 2026-07-17, under the same deadline as
1.10** (see README.md's status line and CHANGELOG) — this whole phase
was originally planned to start only after Phase 5, but P0 needed real
internet exposure today. What actually shipped differs in shape from
6.0/6.1's sketch below: **one** repo-root `docker-compose.prod.yml`
(not `server/docker-compose.prod.yml`) covers all 5 services (`caddy`,
`photo-viewer`, `auth`, `postgres`, `redis`) in a single file — needed
because Caddy has to reverse-proxy to *both* `server/`'s auth backend
and `mamma-photo-viewer`'s separate `app/` codebase, which 6.0's
sketch (written before that split existed) didn't anticipate. The
`Caddyfile` is at the repo root too. 6.2's smoke test and 6.3's UFW
ruleset are both folded into
[DEPLOYMENT.md](DEPLOYMENT.md) instead of being separate steps. The
human checkpoint below (DNS/router/UFW, run by Joakim) had not been
executed as of this session's handoff — check DEPLOYMENT.md and this
file's CHANGELOG entry for current status rather than assuming either
way.

6.0 (superseded, see note above) Add `server/docker-compose.prod.yml`, an override restoring
`restart: unless-stopped` on `app`/`postgres` (the dev base file
deliberately uses `restart: "no"` — see global Docker rule) — only ever
invoked explicitly via `docker compose -f docker-compose.yml -f
docker-compose.prod.yml up -d` on the real host, never auto-loaded.

6.1 Caddy as a Compose service, only one publishing 80/443; app and
postgres stay internal-only. Caddyfile routes `photos.reuterborg.se`
with automatic HTTPS.

6.2 Compose smoke test: bring the stack up, curl `https://localhost`
with cert verification skipped locally, confirm `/health` reachable
through Caddy.

6.3 Write (don't run) a UFW ruleset — 22, 443, 80 only — into
`documentation/photo-server/DEPLOYMENT.md` for manual review.

(human checkpoint, before any DNS/router change) — **done and confirmed,
2026-07-17.** Root domain confirmed untouched (`dig` before/after);
`photos.reuterborg.se` A record live at Inleed; router (EdgeRouter X)
port-forwarding 80/443 configured over the CLI once SSH was enabled (see
HARDWARE.md, DEPLOYMENT.md's Troubleshooting playbook, CHANGELOG for the
full trail — SSH being off by default and a hairpin-NAT gap both cost
real time). Caddy obtained its Let's Encrypt cert automatically once
reachable. Confirmed working from outside the LAN (phone, mobile data)
*and* from the LAN itself (after enabling `hairpin-nat`). `/health` isn't
reachable through the catch-all route as originally written here — that
path goes to the photo-viewer, which has no `/health` route; `/login`
(auth backend) is what was actually used to verify reachability. Real
end-to-end login (not just reachability) also confirmed, after finding
and fixing two more gaps: the Postgres schema was never initialized in
production (nothing in the deploy path ran `ensure_schema` — worked
around live at the time). Both **since fixed for real** (2026-07-18:
`ensure_schema` now runs from a FastAPI `lifespan` handler on startup,
and `server/Dockerfile` now copies `scripts/`) — see
`../bugs/solved/2026-07-17-postgres-schema-never-initialized-in-production-SOLVED.md`
and
`../bugs/solved/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md`.

## Phase 7 — Stability checkpoint

Once Elisabeth has done one real session (browse, search, tag, download
from outside the LAN): the top bar's position and tap-to-add-to-active-
tag as the core gesture are now fixed — changes to those two things need
a reason, not just a preference. Everything else can keep evolving in
small increments (see GUI spec §9, folded in here rather than kept as a
separate file).

## Cross-cutting security checklist

Re-check this list at the end of every phase above, not just once:

- Secrets (DB password, session signing key) come from env vars only,
  never committed — checked at 0.4, re-verify at each phase's commit.
- Every query that returns photo/tag/selection data is scoped to the
  authenticated user via `photo_owners`/`tags.user_id` — no "trust the
  frontend to only ask for its own data."
- Every endpoint that takes a path/filename component has an explicit
  traversal test (`../../etc`), not just a happy-path test.
- Every subprocess invocation (ffmpeg, exiftool) uses an argument list,
  never shell-string interpolation of user-influenced data.
- `audit_log.details` never carries raw GPS/EXIF values — log that an
  action happened, not the sensitive payload itself (ties to POLICY.md's
  location-data rule).
- Rate limiting exists on `/login` (1.8) — confirm at Phase 4/5 whether
  `/photos/search` or `/tags/{tag}/download` need it too once real usage
  patterns are visible; not required for the Sunday deliverable at
  two-user scale, but don't forget to revisit.
- Docker: app container runs as a non-root user; Postgres role used by
  the app has only the privileges it needs on its own schema, not
  superuser.
- Dependency versions pinned (Pillow, ffmpeg, RAW-reading library) —
  these parse untrusted file content (Phase 3.5's note).
- **Systematic discovery pass for this same class of bug** (framework/
  proxy defaults neither of us explicitly chose - the Swagger exposure
  below was exactly this), raised by Joakim 2026-07-18, not started:
  check Caddy's own admin API (`:2019`, confirm localhost-only) and
  FastAPI's default error responses for traceback leaks; run `pip-audit`
  against `pyproject.toml`/`uv.lock` on both services for known
  dependency CVEs; run an OWASP ZAP baseline scan against the live site
  for missing security headers/common injection points. None of the
  three set up yet.
- **Swagger/OpenAPI docs were publicly exposed, unauthenticated — fixed
  and deployed 2026-07-18.** `require_session` was wired per-route via
  `Depends()`, not app-wide, so FastAPI's auto-generated `/docs`,
  `/redoc`, `/openapi.json` bypassed it entirely, and `Caddyfile`
  routed everything except `/login /whoami /refresh /logout` to
  `photo-viewer` - so `/docs` was reachable from the public internet
  with no login. Fixed same-day with `docs_url=None, redoc_url=None,
  openapi_url=None` on both `FastAPI()` instances, TDD'd, redeployed,
  and confirmed live (`curl -I https://photos.reuterborg.se/docs` →
  `404`).
- **Structured security-audit tool, designed 2026-07-18, not built** —
  same idea as `doc_metrics`/`commit_cost`: an append-only, structured
  ledger instead of ad hoc `grep`/`psql` commands re-typed each time.
  What it should check, per run:
  - **Caddy access/error logs**: count and bucket `502`/`401` bursts by
    time, so a restart-triggered spike (like 2026-07-17's, fully
    explained in hindsight) is visually distinguishable from an ongoing
    problem without manually re-deriving the timestamp math each time.
  - **`audit_log` table**: `login_failure` grouped by attempted email,
    `login_success` grouped by user - the two queries used ad hoc
    throughout 2026-07-18's live review.
  - **Host-level logs, not just app/Docker ones** (Joakim, 2026-07-18):
    `sudo` usage and SSH login attempts on the actual server host
    (`/var/log/auth.log` or `journalctl -u ssh`, whichever this Ubuntu
    24.04 box actually uses - confirm, don't assume) - today's review
    only covered app-level logs, missing this entirely.
  - Output as a git-tracked, append-only ledger (jsonl, same pattern as
    `tools/doc_metrics`/`tools/commit_cost`) so trends are visible over
    time, not just a point-in-time snapshot.
  Not started - needs its own TDD design pass, not rushed live.

## Out of scope

See [DEFERRED.md](DEFERRED.md).
