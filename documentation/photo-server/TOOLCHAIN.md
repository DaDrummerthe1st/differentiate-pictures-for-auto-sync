# Toolchain — photo-server

Moved here from `server/README.md` so all photo-server documentation lives under `documentation/photo-server/`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule. This file covers what [README.md](README.md)'s product spec and [TODO.md](TODO.md)'s roadmap don't: the local dev toolchain. All commands below run from the `server/` directory.

## Toolchain: uv, not pip/venv

Dependencies and the virtualenv are managed with [uv](https://docs.astral.sh/uv/), not `pip`/`venv` directly. This wasn't a style preference — the dev machine this was built on has no working `pip` and `python3 -m venv` fails (`ensurepip` missing, no `python3-venv` package installed, and installing one is a system-level change per [POLICY.md](../policies/POLICY.md)). uv vendors its own Python/venv handling, so it sidesteps that gap entirely.

```
uv sync                              # install dependencies into .venv
uv run pytest tests                  # run the test suite
uv run uvicorn app.main:app --reload # run the app locally
```

`server/uv.lock` is committed for reproducibility. Dev-only dependencies (`pytest`, `httpx2`) live in the `dev` dependency group and are excluded from the Docker image via `uv sync --no-dev` (see `server/Dockerfile`).

## Testing against Postgres

`server/docker-compose.yml`'s `postgres` service deliberately never publishes its port to the host (TODO.md 0.2's security line), so it's unreachable from a plain `uv run pytest` on the dev machine. Any step from TODO.md 0.3 onward that touches the database needs a separate, disposable test container instead — not part of the deployed stack, fine to expose on localhost only:

```
server/scripts/test_db.sh up         # start, wait until ready (127.0.0.1:5433)
uv run pytest tests                  # tests/conftest.py connects to it
server/scripts/test_db.sh down       # stop + auto-remove when done
```

`server/tests/conftest.py`'s `TEST_POSTGRES_*` env vars (`HOST`/`PORT`/ `DB`/`USER`/`PASSWORD`) default to match `test_db.sh`'s own defaults, so no `.env` file is needed for the common case.

## Testing against Redis (Phase 1 onward)

Same reasoning as Postgres above, for `docker-compose.yml`'s `redis` service — TODO.md Phase 1's JWT/session tests need a real Redis, not a mock:

```
server/scripts/test_redis.sh up      # start, wait until ready (127.0.0.1:6380)
uv run pytest tests                  # tests/conftest.py's redis_client fixture connects to it
server/scripts/test_redis.sh down    # stop + auto-remove when done
```

`conftest.py`'s `TEST_REDIS_*` env vars (`PORT`/`PASSWORD`) default to match `test_redis.sh`'s own defaults. `JWT_SECRET_KEY` gets a fixed test value directly in `conftest.py` (not `TEST_`-prefixed — nothing reads it except this test suite itself).

## Testing `server/Dockerfile` changes

Any change to `server/Dockerfile` (a new `COPY`, a new dependency baked into the image, etc.) needs a real `docker build` + `docker run` integration test, not just a code review of the diff — a missing `COPY` line is invisible to `uv run pytest tests` since that runs against the source tree directly, never the built image. See `tests/test_dockerfile_build.py` for the pattern (build the image, run something inside it that only works if the change actually landed in the image, assert exit code 0). Decided 2026-07-18 after `scripts/` silently missing from the image went unnoticed until a live deploy (see `documentation/bugs/solved/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md`).

These tests are marked `@pytest.mark.docker` and excluded from the default `uv run pytest tests` run (`pyproject.toml`'s `addopts = "-m 'not docker'"`) — a full image build is too slow to pay on every test run. Run them explicitly whenever `Dockerfile` changes, and before any production deploy that rebuilds the image:

```
uv run pytest tests -m docker
```
