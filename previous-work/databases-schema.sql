-- Schema-only snapshot of databases/app.db, taken 2026-09-05 during the native-app pivot
-- archiving pass. databases/ itself stays entirely gitignored (real personal photo/contact
-- data never gets committed) -- this file is the one derived, non-personal artifact worth
-- tracking: the shape, not the rows. See previous-work/README.md.
--
-- app.db is one shared SQLite file for the whole (now-archived) app: contacts/db.py wrote
-- the two tables below; modules/pictures.py's `pictures`/`locations` tables (see
-- previous-work/pictures-pipeline/pictures.py) are also expected in this file's schema but
-- were never actually created in this particular database -- no folder scan had been run
-- against it yet as of this snapshot.

CREATE TABLE contacts (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            source TEXT,
            raw TEXT NOT NULL,
            first_saved_at TEXT NOT NULL,
            last_saved_at TEXT NOT NULL
        );
CREATE TABLE contact_emails (
            id TEXT PRIMARY KEY,
            contact_id TEXT NOT NULL REFERENCES contacts(id),
            email TEXT NOT NULL,
            UNIQUE(contact_id, email)
        );
CREATE INDEX idx_contact_emails_email ON contact_emails(email);
