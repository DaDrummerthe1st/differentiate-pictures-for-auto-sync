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

**Before Phase 1 starts**: confirm whether Joakim's existing login
implementation (from another project) replaces the spec below or is
adapted into it. Phase 1 as written is a fallback spec, not a locked-in
design.

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
  access-token TTL is short (15 min) so a stolen access-token cookie
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

1.6 (done) Refresh token expires after 12h, access token after 15 min —
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

1.8 6th failed attempt within a minute from the same IP → 429, via
`slowapi`'s Redis-backed limiter on `POST /login` (`"5/minute"`, ported
from buzzkit's `app/core/rate_limit.py`). Test drives 6 requests,
asserts the 6th (not the 5th) is throttled.

1.8 6th failed attempt within a minute from the same IP → 429, via
`slowapi`'s Redis-backed limiter on `POST /login` (`"5/minute"`, ported
from buzzkit's `app/core/rate_limit.py`). Test drives 6 requests,
asserts the 6th (not the 5th) is throttled.

1.9 **Security pass — gaps not in the original spec, add before calling
Phase 1 done:**
 - Cookie flags: `HttpOnly`, `Secure`, `SameSite=Strict` (or `Lax` if
   cross-site redirects are needed — default to `Strict` and only loosen
   with a reason) on both the access and refresh cookies. Test that the
   flags are present, not just that login works.
 - CSRF: cookie-based auth authenticates state-changing POSTs (tag-add,
   download) automatically from any origin unless mitigated.
   `SameSite=Strict` covers most of this for a single-domain app with no
   third-party embeds — confirm that's actually sufficient here rather
   than assuming, given photos.reuterborg.se is the only origin in play.
 - Logout endpoint: **not in the original build plan at all.** Add
   `POST /logout` that revokes the refresh token server-side in Redis
   (ported from buzzkit's `revoke_refresh_token`) — not just clearing
   the cookie client-side, since a stolen refresh token would otherwise
   stay valid for the rest of its 12h regardless of logout. Test: after
   logout, the old refresh cookie no longer authenticates a `/refresh`
   call.
 - `JWT_SECRET_KEY` minimum length/entropy check at startup (buzzkit
   validates ≥32 characters in its config — port that validator), fed
   through `app/config.py`'s fail-fast pattern from 0.4 rather than a
   new mechanism.
 - Password reset: not in scope for Phase 1 (see MOCKUP.md) — confirm
   this is an accepted gap, not a missed requirement.

1.10 (human checkpoint) Log in as both real accounts with real
passwords you set via 1.2's CLI; confirm a wrong password truly fails;
confirm logout truly invalidates the refresh token (old cookie can no
longer refresh).

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
confirm only the new photo is in the second zip.

## Phase 6 — HTTPS and deployment

6.0 Add `server/docker-compose.prod.yml`, an override restoring
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

(human checkpoint, before any DNS/router change)
- `dig reuterborg.se` and `dig photos.reuterborg.se` — confirm only the
  subdomain's A record changes, root domain untouched.
- Add the A record at Inleed, short TTL, confirm current IP via
  whatsmyip.com.
- Run the Caddy/UFW steps manually.
- Forward external 443 to the app host only once 6.2 passes.
- Repeat the `dig` check from outside the LAN once the port-forward is
  live, to confirm the root domain did not become reachable by accident.
- Confirm `https://photos.reuterborg.se/health` works from outside the
  LAN.

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

## Out of scope

See [DEFERRED.md](DEFERRED.md).
