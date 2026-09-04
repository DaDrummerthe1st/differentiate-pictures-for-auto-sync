# Build contacts/: provider-agnostic CSV/vCard import fallback, TDD

Joakim wanted the desktop contacts-fallback pushed forward without ever handing his real
address book to this session — the design settled on a "fill with mock data" button as the
privacy boundary, with real-file testing happening only in his own browser. Built `contacts/`
(new top-level module, mirroring `modules/`'s standalone-library convention): `models.py`'s
normalized `Contact` record, `vcard_import.py` (the genuinely provider-agnostic path — vCard is
what Google/iCloud/Outlook/Apple Contacts all export, and what CardDAV itself returns), a Google
CSV convenience importer, and `matching.py`'s rename detection (matches by email, never by name,
so a renamed contact is a detected event instead of silently breaking a link). 15 tests, TDD
throughout, synthetic fixtures only. Wired into `.githooks/pre-commit` alongside `modules/tests`.

Also shipped a static demo page (`contacts/demo/index.html`) with mock-data/import-CSV/
simulate-rename buttons. **Known bug, disclosed not hidden**: its JS CSV parser splits on plain
commas with no quote-handling, so Joakim's real 121-column export (commas inside quoted address/
notes fields) parsed completely wrong when he tried it — the tested Python `google_csv_import.py`
doesn't have this gap (uses the real `csv` module). Left for the next session to fix, per the
handoff prompt already given: either a real RFC 4180-aware JS parser, or drop the duplicate JS
logic and call the Python parser instead.

- **Doc size**: GLOSSARY.md +844 (Google People API resourceName/syncToken, App Password entries).
