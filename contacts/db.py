"""Persists Contact records into the app-wide SQLite database
(databases/app.db, shared with modules/pictures.py — same file, separate
tables, no cross-module import per contacts/'s standalone-library
convention).

Dedup/merge rule (Joakim, 2026-09-05): match an incoming contact against
what's already stored by email first (the closest thing to a stable
identifier this data has); if it has no email, or no email matches, fall
back to an exact display_name match. A match merges the *whole* record, not
just those two fields - `raw` (every other source column/property) is
unioned, incoming values winning on conflicts, and emails are unioned rather
than replaced. No match at all means insert as new.

Schema (mirrors modules/pictures.py's pictures/locations split - one table
for identity, a child table for the one genuinely multi-valued field):
- `contacts`: id, display_name, source, raw (JSON blob of the full source
  record), first_saved_at, last_saved_at.
- `contact_emails`: id, contact_id, email - a contact can have any number.
"""
import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from contacts.models import Contact

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "databases", "app.db"
)


@dataclass(frozen=True)
class SaveResult:
    contact_id: str
    display_name: str
    status: str  # "new" | "updated" | "unchanged"
    matched_by: str | None  # "email" | "display_name" | None


@dataclass(frozen=True)
class StoredContact:
    id: str
    display_name: str
    emails: list[str]
    source: str
    raw: dict
    first_saved_at: str
    last_saved_at: str


@dataclass(frozen=True)
class ClassifyResult:
    contact: Contact
    status: str  # "new" | "updated" | "unchanged"
    matched_by: str | None  # "email" | "display_name" | None
    existing: StoredContact | None
    merged_raw: dict
    merged_emails: list[str]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            source TEXT,
            raw TEXT NOT NULL,
            first_saved_at TEXT NOT NULL,
            last_saved_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_emails (
            id TEXT PRIMARY KEY,
            contact_id TEXT NOT NULL REFERENCES contacts(id),
            email TEXT NOT NULL,
            UNIQUE(contact_id, email)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contact_emails_email ON contact_emails(email)")


def _find_match(conn: sqlite3.Connection, contact: Contact) -> tuple[str | None, str | None]:
    """Returns (contact_id, matched_by) or (None, None)."""
    if contact.emails:
        placeholders = ",".join("?" for _ in contact.emails)
        row = conn.execute(
            f"SELECT DISTINCT contact_id FROM contact_emails WHERE email IN ({placeholders})",
            contact.emails,
        ).fetchone()
        if row is not None:
            return row["contact_id"], "email"

    row = conn.execute(
        "SELECT id FROM contacts WHERE display_name = ?", (contact.display_name,)
    ).fetchone()
    if row is not None:
        return row["id"], "display_name"

    return None, None


def _existing_emails(conn: sqlite3.Connection, contact_id: str) -> list[str]:
    return [r["email"] for r in conn.execute(
        "SELECT email FROM contact_emails WHERE contact_id = ?", (contact_id,)
    )]


def _load_stored_contact(conn: sqlite3.Connection, contact_id: str) -> StoredContact:
    row = conn.execute(
        "SELECT id, display_name, source, raw, first_saved_at, last_saved_at FROM contacts WHERE id = ?",
        (contact_id,),
    ).fetchone()
    return StoredContact(
        id=row["id"],
        display_name=row["display_name"],
        emails=_existing_emails(conn, contact_id),
        source=row["source"],
        raw=json.loads(row["raw"]),
        first_saved_at=row["first_saved_at"],
        last_saved_at=row["last_saved_at"],
    )


def _classify(conn: sqlite3.Connection, contact: Contact) -> ClassifyResult:
    """Read-only: decides what save_contacts() would do, without writing."""
    contact_id, matched_by = _find_match(conn, contact)
    if contact_id is None:
        return ClassifyResult(
            contact=contact, status="new", matched_by=None, existing=None,
            merged_raw=dict(contact.raw), merged_emails=list(contact.emails),
        )

    existing = _load_stored_contact(conn, contact_id)
    merged_raw = {**existing.raw, **contact.raw}
    merged_emails = list(dict.fromkeys(existing.emails + contact.emails))
    unchanged = (
        existing.display_name == contact.display_name
        and existing.raw == merged_raw
        and set(existing.emails) == set(merged_emails)
    )
    return ClassifyResult(
        contact=contact,
        status="unchanged" if unchanged else "updated",
        matched_by=matched_by,
        existing=existing,
        merged_raw=merged_raw,
        merged_emails=merged_emails,
    )


def classify_contacts(contacts: list[Contact], db_path: str = DEFAULT_DB_PATH) -> list[ClassifyResult]:
    """Dry run of save_contacts() - what would happen, without writing anything."""
    conn = _connect(db_path)
    try:
        _init_db(conn)
        return [_classify(conn, contact) for contact in contacts]
    finally:
        conn.close()


def list_all_contacts(db_path: str = DEFAULT_DB_PATH) -> list[StoredContact]:
    conn = _connect(db_path)
    try:
        _init_db(conn)
        return [_load_stored_contact(conn, row["id"]) for row in conn.execute("SELECT id FROM contacts")]
    finally:
        conn.close()


def _apply(conn: sqlite3.Connection, result: ClassifyResult, now: str) -> SaveResult:
    contact = result.contact
    if result.status == "new":
        contact_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO contacts (id, display_name, source, raw, first_saved_at, last_saved_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (contact_id, contact.display_name, contact.source, json.dumps(result.merged_raw), now, now),
        )
        for email in result.merged_emails:
            conn.execute(
                "INSERT INTO contact_emails (id, contact_id, email) VALUES (?, ?, ?)",
                (str(uuid.uuid4()), contact_id, email),
            )
        return SaveResult(contact_id=contact_id, display_name=contact.display_name, status="new", matched_by=None)

    contact_id = result.existing.id
    if result.status == "updated":
        conn.execute(
            "UPDATE contacts SET display_name = ?, source = ?, raw = ?, last_saved_at = ? WHERE id = ?",
            (contact.display_name, contact.source, json.dumps(result.merged_raw), now, contact_id),
        )
        for email in result.merged_emails:
            if email not in result.existing.emails:
                conn.execute(
                    "INSERT INTO contact_emails (id, contact_id, email) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), contact_id, email),
                )
    return SaveResult(
        contact_id=contact_id, display_name=contact.display_name, status=result.status, matched_by=result.matched_by
    )


def save_contacts(contacts: list[Contact], db_path: str = DEFAULT_DB_PATH) -> list[SaveResult]:
    conn = _connect(db_path)
    try:
        _init_db(conn)
        now = _now()
        results = [_apply(conn, _classify(conn, contact), now) for contact in contacts]
        conn.commit()
        return results
    finally:
        conn.close()
