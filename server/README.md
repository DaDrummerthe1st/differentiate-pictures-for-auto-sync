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
