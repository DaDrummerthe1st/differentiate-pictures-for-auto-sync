# Postgres schema was never initialized in production

Status: **solved 2026-07-18** — real fix built, workaround no longer needed.

## Symptom

Found 2026-07-17, live: every login attempt failed with "Incorrect email or password" even for the just-created account, because the account creation itself failed first with `psycopg.errors.UndefinedTable: relation "users" does not exist`.

## Investigation log

1. Login failing looked like an auth-code bug at first.
2. Traced to account creation itself failing, not login logic.
3. Root cause: nothing in the deploy path (`docker-compose.prod.yml`, `server/Dockerfile`'s `CMD`) ever calls `app.db.ensure_schema()` against the real production database - it's only ever called from `server/tests/conftest.py`'s test fixture.

## Fix applied (workaround, not the real fix)

Worked around live with a one-off `python -c` call to `ensure_schema`, idempotent (`CREATE TABLE IF NOT EXISTS`) so safe to have run. This workaround is now a documented required step in `photo-server/DEPLOYMENT.md`'s step 4 (added same day), so the next fresh deploy doesn't have to rediscover this.

## Real fix

`app/main.py` now calls `ensure_schema` (and commits) from a FastAPI `lifespan` handler, so it runs once at `auth` container startup, every startup, before the app accepts requests - idempotent (`CREATE TABLE IF NOT EXISTS`), so safe on every restart. Test-driven: `tests/test_main_startup.py` mocks `get_connection`/`ensure_schema` and asserts the lifespan handler calls them. `DEPLOYMENT.md` step 4's manual workaround is removed - no longer a required deploy step.
