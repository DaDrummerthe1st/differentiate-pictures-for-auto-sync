# Admin-configurable photo source + per-detector resource benchmarking

**Built 2026-08-08** (the next session referenced below) — Part A and Part B are both implemented,
tested, and locally smoke-tested; see `documentation/curation/TODO.md`'s "Part A/B" entry for the
full status and two further real corrections made during that build: `momfiles` ended up mounted and
selectable too (not excluded, as originally written a few paragraphs down), and `dpfas_media` gets
populated by a real `POST /api/upload` endpoint any logged-in user can drive from the gallery UI, not
by Joakim manually copying files in over SSH as the "Verification" section below originally assumed.
The design below is left as the original reasoning/shape, not rewritten to match what actually got
built — read it as history, not as current instructions.

**Historical note, not current status:** the paragraph below was written when this was "not this
session's build — corrected and saved for next session, per Joakim's explicit token-saving
instruction (2026-08-08)." That instruction and framing applied to the session that wrote this plan,
not to the session that later built it.

## Context

This session built Phase 3 (face detection/YuNet) of the automatic-tagging build plan
(`documentation/curation/TODO.md`). Joakim then redirected scope before Phase 4, and corrected an
initial (wrong) draft of this plan that assumed the local workstation's `docker-compose.yml` dev
environment. **Corrected instruction**: this runs in **production, directly on the home server
(`192.168.1.10`, ZFS `/tank`)**, not the local workstation — real workload/CPU numbers require the
real hardware, not a Docker Desktop dev box, and Joakim wants to see that load directly. This is a
genuine deploy-to-prod step, not a local dev-only exercise like Phase 3 was.

Two requirements, confirmed by Joakim directly (not AskUserQuestion this round — a direct correction
after the first plan draft was rejected):

1. **Source directory**: a new, dedicated directory, `/tank/dpfas_media` (this repo's own name —
   "differentiate pictures for auto sync" — as the folder name; doesn't exist yet, Joakim creates it
   on `.10`). This is where Joakim will put pictures he wants looked at/tagged — mounted read-only
   into the prod `photo-viewer` container, same "app never writes back" convention as today's
   `PHOTOS_HOST_PATH`/`momfiles` mount. Starts **empty** — Joakim populates it by moving files in
   directly via his existing sudo SSH access to `.10` (already-established access, see
   `documentation/curation/TODO.md`'s "/tank test-data convention" section) — no new upload feature.
2. **`/tank/momfiles` (Elisabeth's own space) stays completely untouched** — not read, not mounted
   as an alternate source, not switchable to. The admin source-setting's whole point is to *avoid*
   ever needing to touch that path; `dpfas_media` is a clean, separate, disposable-by-design
   directory Joakim fully controls, exactly like this repo's existing "rest of `/tank` outside
   `momfiles`" testing convention already establishes.

Admin (Joakim, `role="admin"` per Phase 0's JWT role claim) gets a live, DB-backed setting for
"where to load pictures from" that a `member` account can't see or change — kept from the original
ask, just re-scoped to prod's real directory layout instead of workstation-local mounts.

## Part A — Admin-only, live-configurable photo source (prod)

**`docker-compose.prod.yml`** (written for Joakim to apply, never run by an AI session directly
against `.10`, per `POLICY.md`'s deployment rule): add a new read-only bind mount,
`/tank/dpfas_media:/photo-library-root/dpfas_media:ro`, alongside whatever `momfiles` mount already
exists there today for the main gallery (check `documentation/photo-server/TODO.md`/existing prod
compose for that shape before writing this — don't assume). `PHOTOS_LIBRARY_ROOT` env var (new) =
`/photo-library-root`, the fixed boundary directory.

**Backend** (`app/main.py`), same design as the (correct parts of the) original draft, just pointed
at prod's real directory instead of workstation mounts:

- New singleton-row table: `app_settings(id INTEGER PRIMARY KEY CHECK (id = 1), active_source TEXT
  NOT NULL DEFAULT 'dpfas_media', updated_at TEXT NOT NULL)`. Default (and, in prod, realistically
  only) value: `dpfas_media`. `get_active_photos_root()` reads it, resolves
  `PHOTOS_LIBRARY_ROOT / active_source`, re-validates it's a direct child of `PHOTOS_LIBRARY_ROOT`
  (same traversal-guard shape as the existing `resolve_relpath`, `app/main.py:163`) before returning.
- Every current use of the module-level `PHOTOS_ROOT` constant (`resolve_relpath`, `api_tree`,
  `file_summary`, `thumb`, `original`, download — confirm exact call sites via `grep -n PHOTOS_ROOT
  app/main.py` fresh next session, this list may drift) switches to `get_active_photos_root()`.
- `GET`/`PUT /api/settings/photos-source`, both gated `require_session_with_role` +
  `role == "admin"` (403 for `member`, not 404). `GET` returns `{"active": ..., "available": [...]}`
  — `available` built from real subdirectories of `PHOTOS_LIBRARY_ROOT` via `Path.iterdir()`, not a
  hardcoded list, so this stays correct if Joakim later organizes `dpfas_media` into named
  subfolders or adds another mount. `PUT` validates the name is in `available`, upserts, returns the
  new state.
- Frontend: `app/static/app.js` calls `GET /api/settings/photos-source` once on load; 200 reveals a
  new "Inställningar" button in the existing `#moreActionsMenu` dropdown pattern
  (`app/static/index.html`'s `selectModeBtn`/`downloadAllBtn` siblings); 403 renders nothing new. A
  minimal panel: `<select>` of `available` + save, which PUTs and reloads the gallery tree.

**Tests** (`app/tests/test_settings.py`, TDD, local — `app/tests` is fast/in-process, doesn't touch
real `/tank`): member → 403 GET/PUT; admin → 200 GET with a tmp-path-fixture-built `available` list;
PUT unknown name → 400, DB unchanged; PUT known name → persisted, reflected in a follow-up GET;
`api_tree`/`file_summary` reflect the new active source's contents after a switch.

## Part B — Per-detector CPU-time benchmarking, ~100-photo batches (prod)

Unchanged reasoning from the original draft — still valid regardless of environment:

**What's honestly measurable**: per-detector **CPU time** is cleanly attributable —
`detector/main.py` is synchronous/single-process, so `resource.getrusage(resource.RUSAGE_SELF)`
immediately before/after each `detect_blur`/`detect_exposure`/`detect_monochrome`/`detect_faces` call
gives a real per-detector CPU-time delta (stdlib `resource` module, no new dependency). **Memory is
not cleanly attributable per detector** — `ru_maxrss` is a cumulative peak since process start
(mostly YuNet's one-time model-load cost, not a per-photo cost) — report it once per batch as
"peak RSS so far," labeled batch-level, not per-detector, rather than implying false precision.

**`detector/main.py`**: `/detect` gains an opt-in `include_timing: bool = False` query param
(default off, so today's exact-equality response-shape tests in `test_detect.py` keep passing
unmodified). When true: response gains `"timings": {"cpu_time_ms": {"blur": ..., "exposure": ...,
"monochrome": ..., "face": ...}, "peak_rss_kb": ...}`.

**New `app/benchmark_detector.py`**, invoked `docker compose exec photo-viewer python -m
app.benchmark_detector [--batch-size 100]` directly on `.10` (real hardware, real numbers — this is
*why* the whole thing moved to prod). Walks the active source's image files
(`get_active_photos_root()`), POSTs each to `/detect?include_timing=true`, accumulates per-detector
CPU-time totals + wall clock per completed batch, appends one JSON-line summary per batch to
`/data/benchmark.log` (same `analytics_data` volume the SQLite DB lives on — survives restarts),
also printed to stdout. **Doesn't write to the `tags` table** — pure measurement, no side effects
beyond the log file, deliberately kept separate from Phase 5's real (idempotent) orchestration job.
Pure aggregation logic (list of per-photo timing dicts → one batch summary) is a separate,
unit-tested function; HTTP/filesystem glue stays thin, exercised only by the real run on `.10`
itself (there's no local stand-in for "real hardware numbers" — that's the entire point).

**Tests**: `app/tests/test_benchmark_detector.py` — the aggregation function only, no real
HTTP/subprocess involved, runs in the fast local suite same as everything else.

## Verification (next session)

- `.venv-test/bin/python -m pytest app/tests/ detector/tests/ -q` green, including the new tests
  above — all local, no `.10` access needed for this part.
- Joakim creates `/tank/dpfas_media` (empty) on `.10` and applies the `docker-compose.prod.yml`
  mount change himself (per POLICY.md — written commands, not run by the AI session).
- Joakim populates `dpfas_media` with a real batch (e.g. copies `resources/test_pictures/Florida1/`
  or a real personal batch over) and runs `docker compose exec photo-viewer python -m
  app.benchmark_detector --batch-size 100` on `.10` himself; `/data/benchmark.log` gets real
  per-batch `cpu_time_ms` numbers from the actual home-server hardware.
- Confirm `momfiles` is never touched by any of this — no code path reads it, no mount references
  it, no test fixture uses it.
- Update `documentation/curation/TODO.md`/`documentation/tags/SCHEMA.md`/`documentation/GLOSSARY.md`
  and log a changelog entry in the same pass, per this repo's conventions.
