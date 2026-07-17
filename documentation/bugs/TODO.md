# bugs/TODO.md — untriaged

Found, not yet prioritized or placed. See [README.md](README.md) for
how this list works. Entries below are in the order found, not priority
— **start here instead** if picking this up fresh:

1. **Highest-value next step**: "Pre-compile thumbnails ahead of time"
   (below) — the biggest remaining real gap between where this is now
   and Elisabeth having a smooth experience. Three design decisions are
   already identified; start by making those calls, then TDD it.
2. **Quick, safe, worth doing early**: the two deploy-path bugs (Postgres
   schema init, `server/Dockerfile` missing `scripts/`) — both have a
   working documented workaround already (`DEPLOYMENT.md` steps 4-5), so
   this is "wire the known fix into the Dockerfile/CMD properly," not
   fresh investigation.
3. Everything else below (log persistence, resource monitoring, the
   support button, the static-shell-before-login UX) is real but lower
   urgency — the app works for tonight without any of them.

- **Postgres schema was never initialized in production.** Found
  2026-07-17, live: every login attempt failed with "Incorrect email or
  password" even for the just-created account, because the account
  creation itself failed first with `psycopg.errors.UndefinedTable:
  relation "users" does not exist` — nothing in the deploy path
  (`docker-compose.prod.yml`, `server/Dockerfile`'s `CMD`) ever calls
  `app.db.ensure_schema()` against the real production database; it's
  only ever called from `server/tests/conftest.py`'s test fixture. This
  is the actual root cause that made login look broken for a long stretch
  of the P0 deploy — the auth code itself was fine throughout. Worked
  around live with a one-off `python -c` call to `ensure_schema`,
  idempotent (`CREATE TABLE IF NOT EXISTS`) so safe to have run. Real
  fix: an explicit migration/init step in the deploy sequence (either
  call `ensure_schema` once at `auth` container startup, or wire the
  workaround below into the Dockerfile/CMD directly). The workaround
  itself is now a documented required step, not just a memory of what
  happened — see `photo-server/DEPLOYMENT.md`'s step 4 (added same day),
  so the next fresh deploy doesn't have to rediscover this.
- **`server/Dockerfile` never copies `scripts/` into the image.**
  Found 2026-07-17, live during the P0 deploy:
  `docker compose exec auth python -m scripts.create_account ...` fails
  with `ModuleNotFoundError: No module named 'scripts'` — the Dockerfile
  only `COPY`s `app/`, never `scripts/`, so the CLI account-creation tool
  documented in `documentation/photo-server/DEPLOYMENT.md` doesn't
  actually exist inside the running container. Worked around live via an
  inline `python -c` one-liner calling `app.accounts.create_account`
  directly (bypasses the script, uses only what's already in the image).
  Real fix: add `COPY scripts/ /app/scripts/` (and whatever else
  `scripts/create_account.py` imports beyond `app.*`) to
  `server/Dockerfile`, rebuild, and re-verify the documented command in
  DEPLOYMENT.md actually works before trusting that doc again. Until
  then, `photo-server/DEPLOYMENT.md`'s step 5 documents the working
  one-off `python -c` equivalent as the actual required step.

- **Thumbnails fail under concurrent load, likely OOM.** Found
  2026-07-17, live during the P0 human checkpoint. Full investigation
  trail: [reports/2026-07-17-thumbnail-oom-under-load.md](reports/2026-07-17-thumbnail-oom-under-load.md)
  — mitigated (mem_limit 256m->512m) and a real fix applied
  (`MAX_CONCURRENT_THUMBNAILS` semaphore, TDD'd), both same day; report
  has the full trail including what's still unverified under real load.
- **Faster/leaner thumbnail generation** (raised 2026-07-17, ties to the
  above): `Image.draft()` before resize would cut decode cost for JPEG
  sources; `pyvips` is a plausible future alternative to Pillow for
  genuinely lower peak memory on Pi-class hardware. Neither evaluated or
  built - candidate follow-ups once the semaphore fix is confirmed
  sufficient on its own.
- **Pre-compile thumbnails ahead of time, not on-demand** (Joakim,
  2026-07-17, refined from an earlier "background/async" framing to a
  concrete direction): confirmed the semaphore + `Image.draft()` fixes
  helped, but a full album can still "give up" partway through - large
  albums take real cumulative wall-clock time under the semaphore's
  `MAX_CONCURRENT_THUMBNAILS` cap, and something in the chain (browser
  patience, a connection limit) may time out before it finishes. The
  strongest fix, not attempted today: generate every thumbnail once,
  ahead of any user request, so `/thumb` at browse time is *always* a
  cache hit (a cheap file read, current code's existing
  `cache_path.exists()` fast path already does this - the change is
  running that generation path proactively over the whole tree, not
  rewriting it). Real design decisions needed before building, not to be
  guessed at live: (1) where the job runs - in-process at startup
  (mustn't block uvicorn actually serving requests), a separate one-off
  script, or a scheduled job; (2) what handles photos added after the
  initial pass - a periodic re-scan, or keep today's on-demand path as a
  fallback for cache-misses so pre-compiling isn't all-or-nothing; (3)
  whether it needs to be resumable if interrupted mid-batch (a restart,
  a crash) rather than starting over. Don't rush this live against a now-working
  production service - design and TDD it properly next session.
- **No log persistence guarantee across the stack** (Joakim, 2026-07-17,
  explicit requirement: "ALL logs need to be persistent, even docker's").
  Today's `docker-compose.prod.yml` doesn't configure a logging driver at
  all for any of the 5 services, so they use Docker's default (`json-file`
  written to the host under `/var/lib/docker/containers/...`) — this
  *does* survive a container restart, but is lost if a container is
  recreated (e.g. every `up -d --build`, which happened several times
  during today's deploy) and isn't rotated/bounded by anything in this
  repo's own config. Real fix, not attempted today: an explicit logging
  driver + rotation policy (e.g. `json-file` with `max-size`/`max-file`,
  or a bind-mounted log directory) added per-service in
  `docker-compose.prod.yml`, covering all 5 containers - not just the
  app's own `audit_log`/`analytics.db` (which already persist correctly
  via named volumes, confirmed in DEPLOYMENT.md's verify step). Needs
  testing (does a real restart actually preserve them under the new
  config?) before trusting it, same bar as everything else deferred here.
- **No resource monitoring / alerting for the deployed stack.** Raised
  2026-07-17 by Joakim while chasing a broken-thumbnail bug on a
  memory-tight host (3.8GB total, ~1GB "available" under 5 containers -
  see HARDWARE.md). Wants periodic system resource levels (RAM, disk,
  per-container) in the logs, with some kind of flag/alert when
  something's "topped out" (an actual threshold, not just raw numbers to
  eyeball). Not designed yet - needs real decisions before building:
  where do these logs live (a new table? a file? piggyback on
  `analytics.db`?), what counts as "topped" per resource, and what
  happens when the threshold trips (just a log line? something that
  actually notifies Joakim?). Log/monitoring feature, not a quick add.
- **Support/help button, not built** — Joakim's request, live during the
  P0 checkpoint: an always-present, unobtrusive support/help button in
  the photo-viewer UI (rough sketch: round blue button, white question
  mark, out of the way graphically). No spec yet — needs a real design
  pass (what does pressing it actually do? open a help panel, an email
  link, a form?) before it's buildable, same bar as this project's other
  GUI-facing work (see `photo-server/TODO.md`'s MOCKUP.md rule).
- **Unauthenticated static UI shell loads before any login check.**
  Found 2026-07-17, live during the P0 human checkpoint: visiting
  `https://photos.reuterborg.se/` shows the photo-viewer's "choose where
  to download photos" onboarding prompt first, regardless of session
  state — confusing for a non-technical user expecting a login screen.
  Not a security bug (no photo data in that prompt, and the actual data
  endpoints are correctly gated - confirmed via the 401 tests), but a
  real UX rough edge. Root cause: `app/main.py` mounts `StaticFiles` at
  `/` ungated by design (today's P0 only gated the API routes, not the
  shell), so `index.html`/`app.js` always load first; only the first
  data fetch (`/api/tree` etc.) discovers there's no session and
  redirects to `/login` via `app.js`'s `authFetch`. Real fix: client-side
  session check (e.g. a lightweight `/whoami`-style call, or just always
  attempting the redirect-on-401 flow) before rendering the onboarding
  prompt at all, so an unauthenticated visitor lands on `/login` first.
  **Extended 2026-07-17**: this prompt reappears on *every* page refresh,
  even when already logged in and even after previously dismissing it —
  not just on first visit. Worse in Firefox specifically: Firefox doesn't
  support the File System Access API the folder-picker needs, so the
  prompt is pure friction there (the app's own text admits it - "den här
  webbläsaren stöder inte mappval... men du kan fortsätta ändå"). Real
  fix needs product input, not just code: should this be a one-time
  choice persisted (localStorage/cookie), and should unsupported browsers
  skip the prompt entirely rather than show a "your browser can't do
  this" message every time?
