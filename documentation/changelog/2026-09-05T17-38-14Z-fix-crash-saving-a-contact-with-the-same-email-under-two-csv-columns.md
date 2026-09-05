# Fix crash saving a contact with the same email under two CSV columns

Joakim hit a real crash on his first save attempt against his actual export: `sqlite3.IntegrityError:
UNIQUE constraint failed: contact_emails.contact_id, contact_emails.email`. Root cause: a real Google
export can list the same address under two different `E-mail N - Value` columns, and neither
`parse_google_csv()` nor `contacts/db.py`'s new-contact path deduped a contact's emails before
inserting. Fixed at both the source (`google_csv_import.py` dedupes per row) and defensively in
`db.py::_classify()`'s new-contact branch (the matched/merge branch already deduped; the new-contact
branch didn't). 2 regression tests; reproduced and verified fixed end-to-end with synthetic data
mirroring the real shape, never Joakim's actual file.

- **Doc size**: new bug report, 3404 chars.
