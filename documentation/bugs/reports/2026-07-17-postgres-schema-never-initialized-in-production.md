# Postgres schema was never initialized in production

Status: **worked around, real fix not built**.

## Symptom

Found 2026-07-17, live: every login attempt failed with "Incorrect
email or password" even for the just-created account, because the
account creation itself failed first with `psycopg.errors.UndefinedTable:
relation "users" does not exist`.

## Investigation log

1. Login failing looked like an auth-code bug at first.
2. Traced to account creation itself failing, not login logic.
3. Root cause: nothing in the deploy path (`docker-compose.prod.yml`,
   `server/Dockerfile`'s `CMD`) ever calls `app.db.ensure_schema()`
   against the real production database - it's only ever called from
   `server/tests/conftest.py`'s test fixture.

## Fix applied (workaround, not the real fix)

Worked around live with a one-off `python -c` call to `ensure_schema`,
idempotent (`CREATE TABLE IF NOT EXISTS`) so safe to have run. This
workaround is now a documented required step in
`photo-server/DEPLOYMENT.md`'s step 4 (added same day), so the next
fresh deploy doesn't have to rediscover this.

## Real fix, not built yet

An explicit migration/init step in the deploy sequence - either call
`ensure_schema` once at `auth` container startup, or wire the workaround
into the Dockerfile/CMD directly.
