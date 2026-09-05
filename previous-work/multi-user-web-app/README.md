# previous-work/multi-user-web-app/

Everything here is disregarded as code — reference and inspiration only, not built on
top of, not imported from, not deployed. Originally moved to a top-level `archive/`
2026-09-04 on the `test_production1` branch when Joakim asked to restart the project's
implementation from scratch while keeping prior research/design (`documentation/`) and the
standalone `modules/` library live. Relocated here, under `previous-work/`, 2026-09-05
alongside `modules/` and `contacts/` (see [../README.md](../README.md)) when the project
pivoted from a browser-based (PWA) client to a native Android app — see
[../../documentation/VISION.md](../../documentation/VISION.md)'s 2026-09-05 note.

Contains the former `app/`, `server/`, `detector/`, `prototypes/`, and the
deployment plumbing that only existed to build/run them (`docker-compose*.yml`,
`Caddyfile*`, root `Dockerfile`/`.dockerignore`/`requirements.txt`/`.env.example`).

Treat any design decision baked into this code (model picks, schemas, naming,
architecture) as history to weigh, not as something already settled for a future
build — ask before carrying one forward rather than assuming it still applies.

**Known stale references, not yet cleaned up** (harmless — comments/strings only,
nothing executes against a missing path): `tools/wrapup_checklist/run.py` and
`tools/wrapup_checklist/checks.py` still mention `app/tests`/`server/tests` by name
in print statements and docstrings.
