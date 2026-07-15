# server/

FastAPI + Postgres backend for photo-server — see
[documentation/photo-server/](../documentation/photo-server/README.md) for
the product spec and [TODO.md](../documentation/photo-server/TODO.md) for
the build roadmap. This file is just the toolchain note that roadmap
doesn't cover.

## Toolchain: uv, not pip/venv

Dependencies and the virtualenv are managed with [uv](https://docs.astral.sh/uv/),
not `pip`/`venv` directly. This wasn't a style preference — the dev
machine this was built on has no working `pip` and `python3 -m venv`
fails (`ensurepip` missing, no `python3-venv` package installed, and
installing one is a system-level change per
[POLICY.md](../documentation/policies/POLICY.md)). uv vendors its own
Python/venv handling, so it sidesteps that gap entirely.

```
uv sync                              # install dependencies into .venv
uv run pytest tests                  # run the test suite
uv run uvicorn app.main:app --reload # run the app locally
```

`uv.lock` is committed for reproducibility. Dev-only dependencies
(`pytest`, `httpx2`) live in the `dev` dependency group and are excluded
from the Docker image via `uv sync --no-dev` (see `Dockerfile`).

## Testing against Postgres

`docker-compose.yml`'s `postgres` service deliberately never publishes
its port to the host (TODO.md 0.2's security line), so it's unreachable
from a plain `uv run pytest` on the dev machine. Any step from TODO.md
0.3 onward that touches the database needs a separate, disposable test
container instead — not part of the deployed stack, fine to expose on
localhost only:

```
scripts/test_db.sh up                # start, wait until ready (127.0.0.1:5433)
uv run pytest tests                  # tests/conftest.py connects to it
scripts/test_db.sh down              # stop + auto-remove when done
```

`tests/conftest.py`'s `TEST_POSTGRES_*` env vars (`HOST`/`PORT`/`DB`/
`USER`/`PASSWORD`) default to match `test_db.sh`'s own defaults, so no
`.env` file is needed for the common case.
