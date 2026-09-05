import json
from typing import Any

import psycopg


def log_audit_event(
    conn: psycopg.Connection,
    *,
    action: str,
    user_id: int | None = None,
    catalogue: str | None = None,
    filename: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    # details must never carry raw GPS/EXIF values (POLICY.md) - not
    # applicable to the login events this is used for so far, but
    # worth stating at the write path, not just the schema doc.
    conn.execute(
        """
        INSERT INTO audit_log (user_id, action, catalogue, filename, details)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, action, catalogue, filename, json.dumps(details) if details else None),
    )
