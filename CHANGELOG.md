# Changelog

One entry per revision, newest first.

## 2026-07-16 (21)

- Dependency/CVE check across `server/`, prompted by Joakim asking for a
  version update after CVE warnings on other repos — also the first
  application of entry (20)'s new policy, applied retroactively to 0.4.
  `uv lock --upgrade` produced no diff: every dependency (`fastapi`
  0.139.0, `psycopg` 3.3.4, `uvicorn` 0.51.0, `httpx2`/`httpcore2` 2.7.0,
  `pytest` 9.1.1, and transitive deps) was already resolved to its
  newest version, since `pyproject.toml`'s `>=`-only constraints let `uv
  sync` pick latest by default. `pip-audit` (run via `uvx --python 3.13`
  — the system's `/usr/bin/python3.12` lacks a working `ensurepip`, so
  `uvx` needs a uv-downloaded interpreter instead, same gap
  [TOOLCHAIN.md](documentation/photo-server/TOOLCHAIN.md) already notes
  for `uv sync`) found no known vulnerabilities in either the production
  or full (prod+dev) dependency set. Also checked the two pinned Docker
  base images: `postgres:18.4-bookworm` is Docker Hub's current tag and
  is itself the release that fixed 11 CVEs (not one needing a further
  patch); `python:3.12-slim-bookworm` is a floating tag, always latest
  on rebuild. No changes needed. Full suite re-run: 11/11 green.

## 2026-07-16 (20)

- New non-negotiable in `CLAUDE.md`: check for newest dependency
  versions before every numbered TODO step (not just once per phase, and
  not only when a CVE prompts it); if updating surfaces an incompatible
  or breaking newer version, fixing that break is the priority — no
  quiet revert-and-move-on. Joakim's call, made concrete because 0.4 (the
  previous commit) was implemented against already-pinned versions
  without a fresh check first. Granularity (per-step, not per-phase) and
  location (`CLAUDE.md` globally, not scoped to one topic's TODO.md)
  both confirmed with Joakim rather than assumed. Doc character count:
  `CLAUDE.md` 8280 → 8819 (+539).

## 2026-07-16 (19)

- photo-server TODO.md 0.4 (env-var-only DB config, fail-fast on a
  missing var): new `server/app/config.py`'s `load_db_config()` reads
  the five `POSTGRES_*` vars with no fallback defaults and raises
  `MissingConfigError` if any are missing; `app/main.py` calls it at
  module import time so the app refuses to start before binding a port
  rather than failing lazily on the first DB-touching request.
  `app/db.py`'s `get_connection()` now goes through the same loader
  instead of repeating `os.environ[...]` inline. TDD: new
  `tests/test_config.py` (6 tests: happy path, one per missing var,
  plus an import-time-reload check on `app.main`) written failing
  first, then made to pass. Also fixed a real gap this step's tests
  exposed: `docker-compose.yml`'s `app` service defined no `POSTGRES_*`
  environment at all — with the new fail-fast check in place that would
  have kept the real container from starting — now wired through
  against the `postgres` service. Full suite: 11/11 green (was 4/4
  before this step). Doc character counts:
  `documentation/photo-server/TODO.md` 13595 → 14166 (+571),
  `documentation/photo-server/README.md` 4477 → 4700 (+223).

## 2026-07-16 (18)

- Session wrap-up audit: git clean, 33/33 tests green (29 tool + 4
  server), no dangling Docker images/containers, all 24 tracked `.md`
  files' cross-references resolve, lockfile matches manifest, no stale
  FIXME/TODO drift from this session's changes. Two real gaps found and
  fixed separately: the "auto" permission-mode recommendation was never
  actually applied (flagged back to Joakim — needs his `/config` action,
  not something I can do); and this session went the entire way without
  writing anything to the auto-memory store despite substantial feedback
  — fixed by adding two feedback memories (exact-measurements-over-
  estimates; permission-pushback-and-written-policy).
- **Forward-effectiveness note**: this session's `commit_cost` bugs
  (`<synthetic>`-model pricing block, the `tools/*/metrics.py` bare-import
  collision) were only caught because both tool test suites happened to
  get run *together* once. There's no single "run everything" command in
  this repo today — `tools/doc_metrics` + `tools/commit_cost`'s unittest
  suites and the server's pytest suite (behind `test_db.sh up`/`down`)
  are three separate manual invocations. Worth considering a single
  wrapper script next time test infrastructure is touched, so a future
  cross-suite bug doesn't depend on remembering to combine them by hand.
  Not built now — noted as a suggestion, not a decision.

## 2026-07-16 (17)

- Redundancy + doc-location audit, prompted by Joakim asking "is that not
  a rule?" about documentation living under `documentation/`. Checked the
  actual written rule (`CLAUDE.md`'s Documentation layout section) and
  found it only governs `documentation/`'s own internal structure plus
  two explicit exceptions (root `README.md`, `CLAUDE.md`) — it never
  addressed `server/README.md` or the two `tools/*/README.md`s, which had
  drifted into holding real content outside `documentation/`. Per
  Joakim's decision: moved that content in — `server/README.md`'s
  toolchain notes → `documentation/photo-server/TOOLCHAIN.md`;
  `tools/doc_metrics/README.md` and `tools/commit_cost/README.md` → new
  `documentation/tooling/` (project-wide utilities, not tied to one
  topic) — and left one-line stub `README.md`s in the code directories
  for IDE discoverability. Made this an explicit written rule in
  `CLAUDE.md` so it doesn't drift again. Also fixed the one real
  redundancy the audit found: `CLAUDE.md`'s privacy bullet restated
  `POLICY.md`'s EXIF/GPS and distributed-sync specifics instead of
  cross-referencing them, against `POLICY.md`'s own "nothing project-wide
  duplicated outside this file" rule — trimmed to a cross-reference.
  Updated every affected link (six code docstrings, two README index
  tables) and verified all of them resolve. Doc character counts:
  `CLAUDE.md` 7633 → 8280 (+647), `documentation/README.md` 634 → 729
  (+95), `documentation/photo-server/README.md` 4388 → 4477 (+89),
  `server/README.md` 2004 → 241 (-1763, now a stub),
  `tools/doc_metrics/README.md` 6298 → 219 (-6079, now a stub),
  `tools/commit_cost/README.md` 5136 → 219 (-4917, now a stub); new:
  `documentation/photo-server/TOOLCHAIN.md` 2104,
  `documentation/tooling/README.md` 656,
  `documentation/tooling/DOC_METRICS.md` 6712,
  `documentation/tooling/COMMIT_COST.md` 5378.

## 2026-07-16 (16)

- `commit_cost` was documented in its own README but nowhere else —
  found while Joakim asked "is the new metrics and the old metrics
  documented?" Fixed two real gaps: (1) `CLAUDE.md` mandated running
  `doc_metrics`'s `log.py` after every commit but never mentioned
  `commit_cost` at all, so a fresh session with zero prior context
  wouldn't know to keep doing it — added a standing rule mirroring the
  `doc_metrics` one, per Joakim's explicit call to make it a written
  requirement, not just a habit this session picked up; (2) the two
  tools' READMEs only cross-linked one way (`commit_cost` → `doc_metrics`)
  — added the reverse link. Doc character counts: `CLAUDE.md` 7181 → 7633
  (+452), `tools/doc_metrics/README.md` 6103 → 6298 (+195).

## 2026-07-16 (15)

- Added `tools/commit_cost`: exact per-commit token/dollar cost, distinct
  from `doc_metrics` (which measures document *size*, not the cost of
  producing it). Reads Claude Code's own session transcripts
  (`~/.claude/projects/<slug>/*.jsonl`) — every assistant turn's
  `message.usage` carries the actual billed tokens, not an estimate — and
  anchors on each `git commit` tool call's real result hash to sum usage
  exactly between one commit and the next. Per Joakim's explicit
  correction: a human-authored commit (no matching session) logs a real
  `0`, never a null "unknown" — that's what makes human-vs-LLM cost
  comparisons meaningful. `cost_usd` is null only when tokens are known
  but genuinely unpriceable (mixed/unrecognized model in one commit).
  `session_id` captured per commit too (`sessionId` is already on every
  transcript row) for a `report.py --by-session` view. Caught and fixed
  one real bug before trusting it: Claude Code's `<synthetic>`
  (zero-usage, compaction-related) rows were polluting the per-commit
  `models` list and wrongly blocking pricing — regression-tested.
  Verified end-to-end against this repo's real history: 45 LLM-assisted
  commits, 72 human-only, ~$97.72 total. Also fixed a latent bug this
  surfaced: `doc_metrics/test_metrics.py` and `commit_cost/test_metrics.py`
  both did a `sys.path` + bare `import metrics`, which collide in
  `sys.modules` when both suites load in one process — switched to
  qualified imports (`from tools.<name> import metrics`). Doc character
  counts: `tools/commit_cost/README.md` (new) 5136.

## 2026-07-16 (14)

- Clarified `tools/doc_metrics/README.md`'s opening: it only stated the
  mechanical goal (measure char growth consistently) not the actual
  reason Joakim wants it (a cost ledger tied to outcomes/tasks). Fixed
  the framing regardless of the bigger `commit_cost` discussion that
  followed in the same session. Doc character counts:
  `tools/doc_metrics/README.md` 5789 → 6103 (+314).

## 2026-07-16 (13)

- Renamed `metrics.jsonl`'s keys to match `metrics.db`'s column names
  exactly (`ts`→`recorded_at`, `commit`→`commit_hash`, `file`→
  `file_path`, `chars`→`char_count`), per Joakim's readability ask.
  Applied to all 736 existing rows — a pure key-rename, values
  untouched, so kept despite the append-only design (renaming a key's
  spelling isn't rewriting a past entry's meaning). Also clarified for
  Joakim that `metrics.db` was already gitignored (never committed), so
  the jsonl+db split isn't paying a double storage cost in git — only
  `metrics.jsonl` is. Doc character counts:
  `tools/doc_metrics/README.md` 5219 → 5789 (+570).

## 2026-07-16 (12)

- Fixed a real bug in `tools/doc_metrics` found while confirming its
  char/token tracking to Joakim: `discover_md_files` was a raw filesystem
  walk (`root.rglob("*.md")`), so every regular post-commit `log.py` run
  (not `--backfill`, which already used `git ls-tree` correctly) picked
  up vendored `*.md` files inside gitignored `server/.venv/` — license
  files, a bundled FastAPI skill doc. ~21.6% of all summed characters
  logged to date (427,518 of 1,974,536) was this pollution, and it broke
  the tool's own "every snapshot scoped identically" goal since `.venv`
  contents vary per machine/install. Fixed by scoping to `git ls-files`
  instead; historical `metrics.jsonl` rows left as-is (append-only, same
  precedent as the earlier codepoint-vs-`wc -c` switch), documented in
  `tools/doc_metrics/README.md`. Also added `--task` to `log.py` (labels
  a snapshot with the TODO item/outcome it served) and `--by-task` to
  `report.py` (cost grouped by task) — Joakim wants doc growth traceable
  to what it paid for, not just tracked in the aggregate. `uv run
  pytest`/`unittest` both green (14/14); `metrics.db` rebuilt from the
  git-tracked jsonl to pick up the new `task` column. Doc character
  counts: `tools/doc_metrics/README.md` 3662 → 5219 (+1557).

## 2026-07-16 (11)

- Implemented photo-server TODO.md step 0.3: `users` table (id, email,
  password_hash, role, created_at), psycopg3 + raw SQL per Joakim's
  choice over SQLAlchemy/asyncpg (`app/db.py`), TDD round-trip +
  `unique(email)` tests. Also added `scripts/test_db.sh`, a disposable
  Postgres container for local test runs — the committed
  `docker-compose.yml` deliberately never publishes Postgres's port to
  the host, so plain `pytest` had nothing to connect to; documented in
  `server/README.md`'s new "Testing against Postgres" section. Doc
  character counts: `documentation/photo-server/README.md` 4186 → 4388
  (+202), `server/README.md` 1189 → 2004 (+815).

## 2026-07-16 (10)

- Three more global rules added (`~/.claude/CLAUDE.md`), from Joakim
  asking directly what would make communication more effective: doc-drift
  audits become standing practice at every session close (not just
  when asked — this session's three real drifts only got found because
  they were explicitly requested); no placeholder tool calls (a couple
  slipped through this session); denser bookkeeping updates for repeated
  no-news cycles (test → commit → log-metrics → commit ran ~10+ times
  today, each narrated individually).

## 2026-07-16 (9)

- New global rule (`~/.claude/CLAUDE.md`): keep a current-status line in
  each project's entry doc, updated whenever a phase/step completes.
  Prompted by this session's own experience — asked to estimate a fresh
  session's catch-up cost, the answer came out to ~500-800 characters
  specifically because `documentation/photo-server/README.md`'s status
  line had just been fixed from stale ("planning only, no code written
  yet") to current. Generalizing that habit the same way the CHANGELOG
  discipline was generalized earlier today.

## 2026-07-16 (8)

- Session-wrap-up audit: compared TODO.md's Phase 0 wording against what
  was actually built. Found three drifts, all fixed: 0.1 said "pytest +
  httpx" but the actual dev dependency is `httpx2` (Starlette deprecated
  plain `httpx` in `TestClient` — see the 0.1 commit) — reworded to
  "pytest + FastAPI's `TestClient`" instead of naming a library
  underneath it, so this doesn't re-drift if that changes again; 0.2 said
  "curl /health from inside a container" but the actual (and correct)
  checkpoint curled the published port from the host — reworded to match;
  `server/pyproject.toml` still had uv's placeholder description
  ("Add your description here"), never filled in. Char counts
  (codepoints): `TODO.md` 13488 → 13595 (+107).

## 2026-07-16 (7)

- Checked the no-auto-restart Docker rule from entry (6) against Docker's
  own docs rather than assume it was "best practice" — it isn't one
  Docker prescribes at all (their only stated guidance is "use restart
  policies, avoid process managers"); it's a deliberate, stricter-than-
  typical choice for this project's specific threat (silent re-exposure
  on an untrusted network), not an industry default. Refined the global
  rule (`~/.claude/CLAUDE.md`) to the actual right shape: dev base file
  stays `restart: "no"`, production restores `unless-stopped` via a
  separate Compose override file (`compose.prod.yaml`-style) invoked
  only explicitly at deploy time — Compose auto-loads
  `compose.override.yaml` and nothing else, so this can't activate by
  accident. Added a pointer for this at TODO.md's new step 6.0, so
  Phase 6 doesn't forget it. Char counts (codepoints): `TODO.md`
  13154 → 13488 (+334).

## 2026-07-16 (6)

- Cross-project finding: `buzzkit-api`'s `worker` container had been
  crash-looping (~24h) on missing `JWT_SECRET_KEY`/`COOKIE_DOMAIN` env
  vars. Documented (not fixed, not committed — a different repo, and
  Joakim declined the in-session commit) in that project's own
  `api/README.md`/`CHANGELOG.md`. Logging it here too, since the
  cross-repo rules below only exist in `~/.claude/CLAUDE.md`, which
  isn't tracked in any repo — this entry is the searchable, per-project
  record of what changed and why.
- New global rules added to `~/.claude/CLAUDE.md` (this session, prompted
  by the buzzkit finding above): (1) no dev/test Docker service gets an
  auto-restart policy (`restart: "no"`/omitted, not `unless-stopped`/
  `always`) by default — a container that silently comes back after a
  daemon restart or reboot is a real exposure risk (e.g. reconnecting on
  open wifi without knowing something's listening); (2) committing to a
  repo other than the one a session is rooted in always needs asking
  first, every time, even though committing *within* the active project
  stays standing-authorized; (3) cross-project findings go into the
  target project's existing docs structure (README/TODO/CHANGELOG), not
  a new dedicated inbox file — decided over standardizing one, since
  most projects already have a place this fits.
- Fixed `server/docker-compose.yml` to comply with rule (1) above:
  both `app` and `postgres` were `restart: unless-stopped`, now
  `restart: "no"`.

## 2026-07-16 (5)

- Closed two documentation gaps found on an explicit audit pass ("what's
  undocumented"): added `server/README.md` explaining why `server/` uses
  uv instead of pip/venv (this dev machine's `ensurepip`/`python3-venv`
  is broken — previously only mentioned in passing in TODO.md), and
  generalized the README.md↔HARDWARE.md circular-reference bug fixed
  earlier this session into a durable rule in CLAUDE.md's lean/exact
  bullet ("cross-references must terminate"). Char counts (codepoints):
  `CLAUDE.md` 6829 → 7181 (+352), `server/README.md` 0 → 1189 (new).

## 2026-07-16 (4)

- Merged `photo-server-planning` into `master` (fast-forward, no
  conflicts) per Joakim's specified procedure: pull the feature branch,
  pull master, merge master into the feature branch first, only then
  fast-forward master onto it. Fixed a stale status line in
  `documentation/photo-server/README.md` — it still said "planning only,
  no code written yet" after 0.1 and 0.2 were both built and
  checkpointed this session. Char counts (codepoints): `README.md`
  4031 → 4186 (+155).

## 2026-07-16 (3)

- Step 0.2 human checkpoint passed: Joakim ran `docker compose up --build`
  (after stopping an unrelated stray container, `buzzkit-api`'s
  `api-api-1`, that had squatted on port 8000 for 23h) and confirmed
  `curl /health` returns 200 `{"status":"ok"}` with no `Server` header.
  Postgres 18.4 initialized cleanly at `/var/lib/postgresql/18/docker`,
  confirming the volume-path fix. Phase 0 scaffold (0.1 + 0.2) is done.

## 2026-07-16 (2)

- Added a "Branching and merging" rule to CLAUDE.md at Joakim's request:
  ask and suggest a new branch before starting non-trivial new dev work,
  and never merge into main without confirmation each time. Merging
  differs from push/force-push/history-rewrite (always handed over as a
  copyable command) — once Joakim confirms a merge, the AI session runs
  it directly rather than handing it back. Scoped to this repo, not the
  new global `~/.claude/CLAUDE.md`, per Joakim's answer. Char counts
  (codepoints): `CLAUDE.md` 6178 → 6829 (+651).

## 2026-07-16

- Fixed `server/docker-compose.yml`'s postgres volume mount: it targeted
  `/var/lib/postgresql/data`, the pre-18 convention, which postgres:18+
  refuses to start against (`pg_ctlcluster`-style versioned layout now
  expected). Root cause was a research gap I should have caught before
  writing the file, not a new discovery — 0.2's own commit already cited
  a web search noting "PostgreSQL 18 using /var/lib/postgresql/18/docker"
  but that fact never got applied to the actual mount path. Confirmed
  the fix (mount at `/var/lib/postgresql`, not `.../data`) against
  docker-library/docs's postgres content.md before changing it, rather
  than guessing a second time. Found via Joakim running the step 0.2
  checkpoint himself and hitting the failure.

## 2026-07-15 (13)

- Wrote and built (not run) photo-server TODO.md step 0.2: `server/Dockerfile`
  (multi-stage uv build per Astral's documented pattern, non-root
  `appuser`, `uvicorn --no-server-header` closing 0.1's tracked header
  leak — confirmed the flag exists via `uvicorn --help` before using it),
  `server/docker-compose.yml` (`app` published to 127.0.0.1 only,
  `postgres:18.4-bookworm` with no published port, both with explicit
  `mem_limit`, `POSTGRES_PASSWORD` required via `.env` with no
  hardcoded/blank fallback), `.dockerignore`, `.env.example`. Verified
  postgres 18.4 is current stable via web search rather than assuming a
  version. Image builds clean (201MB, confirmed non-root user and CMD by
  inspecting the built image). `docker compose up` and the curl smoke
  test are still Joakim's to run — both the standing human-checkpoint
  rule and HARDWARE.md's unconfirmed-RAM-upgrade gate apply. Confirmed
  with Joakim that the machine this session runs on is a separate dev
  box from the actual target host (192.168.1.10) — see HARDWARE.md.

## 2026-07-15 (12)

- Fixed two photo-server doc gaps found while explaining the deployment
  environment to Joakim: README.md and HARDWARE.md pointed at each other
  for the "why Docker Compose, not native install" reasoning without
  either stating it — a circular reference, not an actual cross-link.
  HARDWARE.md is now the canonical owner of that reasoning (shared ZFS
  pool → dependency/root-access collision risk), README.md points to it
  one-way. Separately, TODO.md step 0.2's human checkpoint didn't
  reference HARDWARE.md's "don't run `compose up` until the RAM upgrade
  is memtested" gate — a session reading only TODO.md (the file its own
  README tells you to start with) could miss it; added an explicit
  pointer. Char counts (codepoints): `README.md` 4016 → 4031 (+15),
  `HARDWARE.md` 936 → 1129 (+193), `TODO.md` 12977 → 13154 (+177).

## 2026-07-15 (11)

- Implemented photo-server TODO.md step 0.1 (`GET /health`) via TDD:
  failing pytest first, then the minimal FastAPI route. System had no
  `pip`/working `venv` (`ensurepip` missing, no `python3-venv` package) —
  a system-level install per POLICY.md, so handed the fix to Joakim as a
  copyable `apt install` command; he redirected to `uv` instead, which
  needs no system package and resolved everything into `server/.venv`.
  New `server/` is a self-contained uv project (`fastapi`, `uvicorn`,
  `pytest`, `httpx2` — not plain `httpx`, since Starlette's `TestClient`
  now deprecates it in favor of `httpx2`, confirmed by reading
  `starlette/testclient.py` rather than assuming). Manually ran the app
  and curled it for real (TestClient can't see this, since it bypasses
  the transport layer) and found uvicorn's default `Server: uvicorn`
  header leaks the stack, failing 0.1's own Security line; rather than
  fix it in-place (scope belongs to whichever step defines the real run
  command), added a tracked note to TODO.md step 0.2 to launch with
  `server_header=False`. Char counts (codepoints): `TODO.md` 12629 →
  12977 (+348).

## 2026-07-15 (10)

- Trimmed two cross-file/within-file duplications found while auditing
  `documentation/` for excess length at Joakim's request: `VISION.md`
  Pillar 3 fully restated the closed-vs-opt-in trust-boundary tension
  already owned by `POLICY.md`'s Open questions section (POLICY.md's own
  rule: nothing project-wide duplicates outside it) — now a one-line
  pointer. `photo-server/README.md` repeated its own Non-negotiables
  Postgres/pgvector reasoning in its closing paragraph — now stated
  once. No information removed, only the second copy of each fact.
  Char counts (codepoints): `VISION.md` 3718 → 3483 (−235),
  `photo-server/README.md` 4057 → 4016 (−41); −276 net.

## 2026-07-15 (9)

- Fixed a scope mismatch Joakim spotted by auditing every root
  `documentation/` folder against its own stated purpose:
  `photo-server/DPFAS_VISION.md` opened with "the standing goal across
  the whole project," directly contradicting its own folder's README
  ("one narrow, closed slice... nothing here should grow toward...
  AI-driven curation suggestions"), and its three-UX-path table
  duplicated `DATA_DICTIONARY.md`'s Tag-dimensions table in the same
  folder. Deleted the file (per Joakim's choice among three options
  offered); its only non-duplicated content — the Postgres/pgvector
  rationale — moved into `photo-server/README.md`'s existing
  "Relationship to the wider vision" section; the "standing goal" framing
  and three-path breakdown now live in `VISION.md`'s Pillar 2, the
  correct project-wide home. Updated the three other files that linked
  to the deleted file (`VISION.md`, `photo-server/DEFERRED.md`,
  `picture-handling/TODO.md`) to point at `VISION.md` Pillar 2 instead.
  Audited every other file in every root folder against its own folder's
  stated scope; found no other mismatches. `documentation/`: 39,976 →
  39,215 characters.

## 2026-07-15 (8)

- Untracked 5 `.pyc` files under `app/*/__pycache__/` that were
  committed before `__pycache__/` was added to `.gitignore` last
  entry — `git rm --cached`, files kept on disk. Confirmed via
  `git ls-files -i -c --exclude-standard` that nothing else tracked
  matches any `.gitignore` pattern.
- Researched current CVEs (real web search, not training-data guesses)
  for every package in `requirements.txt`, which had no version pins at
  all, and pinned each to the latest patched release: `Pillow==12.3.0`
  (fixes CVE-2026-25990, CVE-2026-42308, CVE-2026-42309, CVE-2026-55379,
  CVE-2026-55380), `mysql-connector-python==9.7.0` (well past
  CVE-2024-21272 and CVE-2025-21548), `numpy==2.5.1`, `opencv-python==5.0.0.93`
  (bundles a libwebp/libvpx build; 5.0.0.93 is current),
  `exif==1.6.1` and `python-magic==0.4.27` (both already the latest
  release on PyPI — no newer version exists, no known CVEs found for
  either). **Unverified**: this sandbox has no `pip`/`ensurepip`, so
  none of this could actually be installed and run against `app/` —
  numpy 2.x and opencv-python 5.x are major version bumps with real
  breaking-change risk (numpy 2.0's ABI break in particular). Flagged in
  `picture-handling/TODO.md`'s Known Drift for Joakim to verify on a
  machine with pip before trusting it. Also noted, but deliberately not
  acted on (system-level, outside this session's authority per
  POLICY.md): Python 3.12.13 is the current security-patch release for
  this repo's 3.12 branch, vs. the 3.12.3 recorded in
  `photo-server/HARDWARE.md`.
  `documentation/`: 39,441 → 39,976 characters.

## 2026-07-15 (7)

- Added `tools/doc_metrics/`: TDD'd (stdlib `unittest`, pytest isn't
  installed in this environment) character-count logging so the
  character-count-change rule is measured the same way every time
  instead of ad hoc `wc -c`. `metrics.py` counts Unicode codepoints per
  `*.md` file; `log.py` snapshots the current commit (or `--backfill`s
  the full history via read-only `git show`/`git ls-tree`, never
  touching the working tree); `report.py` prints char count, delta, and
  an approximate token count (chars/4, explicitly labeled as directional
  only — real cost also depends on current model pricing, not tracked
  here) per commit. `metrics.jsonl` is git-tracked (the durable record,
  per the self-sufficiency rule); `metrics.db` (SQLite) is gitignored,
  local, and rebuildable from the jsonl via `--rebuild-db`. Backfilled
  all 77 existing commits. Also fixed two `.gitignore` gaps found while
  doing this: `.claude/settings.local.json` was untracked but not
  ignored (risk of accidentally committing local permission config), and
  `__pycache__/` wasn't ignored anywhere. Corrected the character-count
  methodology itself: earlier entries in this file used `wc -c` (byte
  count), which runs ~0.8% high on this repo's docs because of em
  dashes; from here on, counts are Unicode codepoints via this tool —
  noted as a one-time methodology switch, not a discrepancy to chase.
  `documentation/`: 39,113 characters (codepoint count, not directly
  comparable to prior entries' byte counts). `CLAUDE.md`: 6,178
  characters.

## 2026-07-15 (6)

- Captured Joakim's long-term system vision (four pillars: distributed
  storage/DFS with a blockchain-like stability mechanism, metadata/
  search/curation, presentation and event-based sharing with an opt-in
  privilege-for-data-sharing model, and multi-angle event reconstruction)
  in a new project-wide `documentation/VISION.md`, cross-linked from
  `distributed-sync/README.md`, `photo-server/README.md`,
  `photo-server/DPFAS_VISION.md`, and the top-level `documentation/
  README.md` index, rather than duplicated into any of them. Flagged
  Pillar 3's opt-in-sharing model as an open tension against the current
  closed-by-default posture in `POLICY.md`'s open questions. Added the
  Sunday deadline's real context to `photo-server/README.md`: a memorial
  for Per, Elisabeth's mother's late partner, where she wants to pick
  photos from ripped CDs/DVDs for a picture-frame USB stick — this is
  why v1 stops at browse/search/tag/download and nothing more.
  `documentation/`: 33,899 → 39,441 characters.

## 2026-07-15 (5)

- Absorbed two external planning documents (a photo-server build plan and
  a GUI-spec amendment, both supplied in chat) into a new
  `documentation/photo-server/` topic folder: README, TODO (the granular
  TDD roadmap), HARDWARE, DATA_DICTIONARY, DEFERRED, DPFAS_VISION, and
  MOCKUP (bare-minimum login + thumbnail-screen written spec, no code).
  Sequenced the roadmap so login (Phases 0–1) is complete before any
  photo/catalogue work starts, per Joakim's priority. Flagged one
  inference for confirmation: the original `selections` table is treated
  as dropped in favor of the GUI spec's tag-based (`kind='album'`)
  mark/download mechanism, since both solved the same problem — see
  DATA_DICTIONARY.md. Superseded the "first MVP/POC, purpose undefined"
  item and its speculative UI/database/AI sections in
  `picture-handling/TODO.md` with a pointer to the new folder, now that
  the purpose is decided. Added two CLAUDE.md rules: report the
  character-count change for every documentation edit, and tightened
  "Lean and compact" into "Lean, exact, and compact." Done on a new
  `photo-server-planning` branch, not master, per Joakim's request.
  `documentation/`: 8,249 → 33,899 characters. `CLAUDE.md`: 5,624 → 5,986
  characters.

## 2026-07-15 (4)

- Second pass on the same documentation trim, per Joakim's answers to a
  few judgment calls: dropped the "In use?" column from both external-
  tools tables (all rows read "Not yet" — zero information), tightened
  a couple more sentences, and removed the sudo/deployment rule
  restatement from CLAUDE.md's high-blast-radius list in favor of a
  pointer to POLICY.md's "Deployment and system access" section (POLICY.md
  already declares itself the sole home for that rule). Declined:
  merging each topic's README+TODO into one file (keeps the documented
  structure rule intact) and resolving the "4D" placeholder in
  `picture-handling/TODO.md` (still unclear — left as-is).
  8,430 → 8,249 characters in `documentation/`.

## 2026-07-15 (3)

- Trimmed `documentation/` for redundancy: the "roadmap addendum
  expected from Joakim" note was stated near-verbatim in three files
  (distributed-sync README, its TODO, and POLICY.md) — now stated once
  in TODO.md's open question, with the other two pointing at it. Also
  de-duplicated a NAS-spec restatement and a security/privacy-posture
  restatement, and tightened wordy passages in `picture-handling/TODO.md`
  and the top-level `documentation/README.md`. No meaning changed; the
  SETI@home analogy was deliberately kept since it's the origin of the
  idea, not just flavor text. 8,950 → 8,430 characters.

## 2026-07-15 (2)

- Noted the next session's starting point in
  `documentation/picture-handling/TODO.md`: build the first frontend
  MVP/POC, operating on pictures already on this server, for a specific
  purpose still to be defined with Joakim. No code written this session.

## 2026-07-15

- Initialized the working-agreement and documentation structure:
  `CLAUDE.md` (non-negotiables + high-blast-radius definition), root
  `README.md`, `documentation/` (policies, picture-handling,
  distributed-sync), and this changelog. Retired `docs/` and
  `resources/for documentation/`, folding their content into the new
  structure. Done to make the repo self-sufficient for future sessions
  instead of relying on AI memory.
