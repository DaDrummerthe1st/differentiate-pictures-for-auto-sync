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
first (pytest + httpx), then the minimal FastAPI route to pass it.
**Security**: response leaks no version/stack info.

0.2 Dockerfile (slim base) + docker-compose.yml with two services: `app`
(bound to 127.0.0.1 only, explicit `mem_limit`) and `postgres` (official
image, explicit `mem_limit`, named volume, conservative
`max_connections`/`shared_buffers`). Compose smoke test: build the
image, curl `/health` from inside a container. **Security**: no ports
published except through the app service; no default/blank Postgres
password — generated and passed via env var, never hardcoded. Also carried
over from 0.1: uvicorn's default `Server: uvicorn` response header leaks
the stack — the Dockerfile `CMD`/compose command must launch uvicorn with
`server_header=False` (confirmed via `uv run uvicorn app.main:app` + curl
against 0.1's route that the default leaks this; TestClient can't catch
it since it bypasses the real transport). (human checkpoint: run the
smoke test yourself, confirm the curl response.)

0.3 `users` table only (id, email, password_hash, role, created_at) —
nothing else from the full schema yet. Test: round-trip insert/read,
`unique(email)`. **Security**: `password_hash` column never appears in
any log statement or test assertion output in plaintext-adjacent form.

0.4 All paths and DB connection details from environment variables only
— test that a missing required env var fails startup immediately
(fail-fast) rather than falling back to a default. **Security**: confirm
`.env`-style files are gitignored before this step's commit, not after.

## Phase 1 — Complete login system (priority one)

1.1 Password hashing helper: hash + verify round-trip test, using
bcrypt. **Security**: confirm bcrypt (not a fast hash like sha256/md5)
before writing it, don't assume the library choice.

1.2 CLI (`server/scripts/create_account.py` or similar) creates the two
accounts — joakim.reuterborg@gmail.com (admin),
elisabeth.reuterborg@gmail.com (member) — bcrypt-hashed, password
supplied interactively or via env var at creation time, never hardcoded
in the repo. Test: CLI creates a row, duplicate email rejected.

1.3 `POST /login` with correct email+password → session cookie, 200.
Test first.

1.4 `POST /login` with wrong password → 401. Same status/body/timing
profile for "wrong password" and "unknown email" — explicit test
comparing both, so the response never discloses whether an email is
registered.

1.5 Unauthenticated request to a protected route → 401. Valid session
cookie → allowed through.

1.6 Sessions expire after 12h — test with a mocked clock, not a real
sleep.

1.7 Failed logins are written to `audit_log`. Test: one failed login →
one row, correct `action`/`details`.

1.8 6th failed attempt within a minute from the same IP → 429. Test
drives 6 requests, asserts the 6th (not the 5th) is throttled.

1.9 **Security pass — gaps not in the original spec, add before calling
Phase 1 done:**
 - Session cookie flags: `HttpOnly`, `Secure`, `SameSite=Strict` (or
   `Lax` if cross-site redirects are needed — default to `Strict` and
   only loosen with a reason). Test that the flags are present, not just
   that login works.
 - CSRF: cookie-based sessions authenticate state-changing POSTs
   (tag-add, download) automatically from any origin unless mitigated.
   `SameSite=Strict` covers most of this for a single-domain app with no
   third-party embeds — confirm that's actually sufficient here rather
   than assuming, given photos.reuterborg.se is the only origin in play.
 - Logout endpoint: **not in the original build plan at all.** Add
   `POST /logout` that invalidates the session server-side (not just
   clears the cookie client-side) — a session store that can't be
   revoked early is a real gap on a machine reachable from the open
   internet. Test: after logout, the old cookie no longer authenticates.
 - Password reset: not in scope for Phase 1 (see MOCKUP.md) — confirm
   this is an accepted gap, not a missed requirement.

1.10 (human checkpoint) Log in as both real accounts with real
passwords you set via 1.2's CLI; confirm a wrong password truly fails;
confirm logout truly invalidates the session.

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
