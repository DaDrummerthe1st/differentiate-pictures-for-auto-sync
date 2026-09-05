# contacts/

A standalone contacts-import library — the file-based, zero-external-connection fallback for
[documentation/tags/TODO.md](../documentation/tags/TODO.md)'s "Contacts import" feature (name
suggestions while face-labeling, see
[documentation/curation/IDENTITY_MATCHING.md](../documentation/curation/IDENTITY_MATCHING.md)).
Deliberately no dependency on `modules/` (though it shares that module's SQLite file, see `db.py`
below) or any other code in this repo, same convention as that directory. Everything here reads a
file the user exported themselves — no live account connection, no OAuth, no credentials of any
kind; the separate live-sync path (Google People API or CardDAV, still undecided) is a different,
not-yet-built feature.

- `models.py` — `Contact`: the provider-agnostic normalized record every importer below produces,
  so matching/rename-detection/persistence logic is written once, not per provider. Beyond the
  identity fields (`display_name`, `emails`, `source`), `raw` holds the *entire* original source
  record (every CSV column, every vCard property) — kept so dedup/merge in `db.py` can compare
  whole records, not just two fields.
- `vcard_import.py` — `parse_vcard()`, the actually provider-agnostic importer: vCard (RFC 6350) is
  the one interchange format every major contacts provider (Google, iCloud, Outlook, Apple
  Contacts) can export, and what CardDAV itself returns under the hood — this parser is reusable
  for a future live-CardDAV path too, not just file import. Uses `vobject` (Apache-2.0).
- `google_csv_import.py` — `parse_google_csv()`, a convenience importer for Google Contacts'
  specific CSV export format, for users who don't know to export vCard instead.
- `matching.py` — `detect_renames()`: matches two contact snapshots by **email**, never by name,
  so a contact renamed between imports (e.g. "Per Holmgren" → "Per H.") is a detected, reviewable
  event instead of silently breaking whatever local person-entity was linked to it. Email is the
  closest thing to a stable identifier a CSV export gives us — no true permanent ID like a vCard's
  `UID` field or the Google People API's `resourceName` (see
  [documentation/GLOSSARY.md](../documentation/GLOSSARY.md)).
- `db.py` — persists `Contact` records into `databases/app.db`, the same SQLite file
  `modules/pictures.py` uses (separate `contacts`/`contact_emails` tables, no shared code — one
  database file for the whole app rather than one per module, decided 2026-09-05). Dedup/merge rule
  (Joakim's call): match an incoming contact by **email** first; if it has none, or none match,
  fall back to an exact **display_name** match; either way, a match merges the *whole* record
  (`raw` unioned, incoming value wins on a conflicting field; emails unioned, never replaced) —
  never a rename/overwrite that discards fields only present in the older or newer import. No match
  at all inserts a new contact. `classify_contacts()` is the read-only dry run of that same logic
  (what `save_contacts()` would do, without writing) — used to render a preview before committing.
- `render.py` — pure-Python HTML rendering (grouping by first letter, per-contact diff view,
  the three page templates) — no client-side JS, no template engine dependency.
- `multipart.py` — `extract_uploaded_file()`, a small `email`-module-based multipart/form-data
  parser (Python 3.13 removed the old `cgi` module this used to be done with) so a plain HTML
  `<form enctype="multipart/form-data">` can upload a file without any JS.
- `web/server.py` — a local-only HTTP server (stdlib only, no framework). Run it yourself with
  `python3 -m contacts.web.server`, then open `http://127.0.0.1:8765/`. Everything is server-
  rendered: `GET /` (upload form) → `POST /preview` (parses the file, classifies it against
  `app.db`, renders the preview — nothing saved yet) → `POST /save` (persists via `save_contacts()`)
  → `GET /contacts` (browses everything currently stored). No fetch/AJAX, no business logic in the
  browser — plain form submissions and full-page HTML responses throughout. Nothing goes past
  127.0.0.1, and no Claude Code session has access to this server or anything sent to it.

## Status

Built 2026-09-05, TDD throughout (tests against synthetic fixture data only — no real exported
file has ever been read by this session, per Joakim's explicit privacy requirement). Started as a
static demo page with an in-memory-only preview; rebuilt same day into the real thing once Joakim
confirmed the CSV parsing worked against his actual export: real SQLite persistence in the shared
`app.db` (renamed from `pictures.db` the same day, since it's no longer picture-only), a genuine
dedup/merge rule operating on full records rather than just email/display_name, and a server-
rendered web UI (`web/`, renamed from the original `demo/` — this is production code now, not a
mockup) with zero client-side JavaScript. Not yet wired into `entities`/`tag_references` (those
tables don't exist anywhere yet — see `documentation/tags/SCHEMA.md`) or into any face-labeling UI
— see IDENTITY_MATCHING.md's "Contacts-import desktop fallback" section for what's still open
(live-sync provider choice, the actual entity-linking step). vCard import (`vcard_import.py`) has
no web UI path yet — only reachable via the Python API directly; the web server currently only
accepts Google's CSV format.
