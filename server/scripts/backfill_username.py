#!/usr/bin/env python3
"""One-time migration for accounts that predate the users.username column
(2026-08-13) - assigns each of them an opaque username in place, instead
of deleting and recreating accounts (see
documentation/bugs/claude-bugs/fixed/2026-08-13-recommended-raw-destructive-sql-against-production-instead-of-a-controlled-script.md
for why that path was wrong). Safe to run whether or not any row actually
needs it - a no-op prints nothing to change.

Run this before auth's next startup if it's crash-looping on
ensure_schema()'s "column username of relation users contains null
values" (NotNullViolation) - that error means at least one row predates
the column. Bypasses the crashing uvicorn entrypoint entirely by running
as a one-off container from the same image:

    docker compose -f docker-compose.prod.yml run --rm auth python -m scripts.backfill_username
"""

import sys

from app.db import backfill_missing_usernames, get_connection


def main() -> int:
    with get_connection() as conn:
        assigned = backfill_missing_usernames(conn)
        conn.commit()

    if not assigned:
        print("Every account already has a username - nothing to do.")
        return 0

    for user_id, username in assigned:
        print(f"user {user_id}: username={username}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
