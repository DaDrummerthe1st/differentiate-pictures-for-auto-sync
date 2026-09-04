# archive/

Everything here is disregarded as code — reference and inspiration only, not built on
top of, not imported from, not deployed. Moved here 2026-09-04 on the
`test_production1` branch when Joakim asked to restart the project's implementation
from scratch while keeping prior research/design (`documentation/`) and the
standalone `modules/` library live.

Contains the former `app/`, `server/`, `detector/`, `prototypes/`, and the
deployment plumbing that only existed to build/run them (`docker-compose*.yml`,
`Caddyfile*`, root `Dockerfile`/`.dockerignore`/`requirements.txt`/`.env.example`).

Treat any design decision baked into this code (model picks, schemas, naming,
architecture) as history to weigh, not as something already settled for the
restart — ask before carrying one forward rather than assuming it still applies.

**Known stale references, not yet cleaned up** (harmless — comments/strings only,
nothing executes against a missing path): `tools/wrapup_checklist/run.py` and
`tools/wrapup_checklist/checks.py` still mention `app/tests`/`server/tests` by name
in print statements and docstrings.
