# contacts/

A standalone contacts-import library — the file-based, zero-external-connection fallback for
[documentation/tags/TODO.md](../documentation/tags/TODO.md)'s "Contacts import" feature (name
suggestions while face-labeling, see
[documentation/curation/IDENTITY_MATCHING.md](../documentation/curation/IDENTITY_MATCHING.md)).
Deliberately no dependency on `modules/` or any other code in this repo, same convention as that
directory. Everything here reads a file the user exported themselves — no live account connection,
no OAuth, no credentials of any kind; the separate live-sync path (Google People API or CardDAV,
still undecided) is a different, not-yet-built feature.

- `models.py` — `Contact`: the provider-agnostic normalized record (`display_name`, `emails`,
  `source`) every importer below produces, so matching/rename-detection logic is written once,
  not per provider.
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
- `demo/server.py` — a local-only HTTP server (stdlib only, no framework) backing `demo/index.html`.
  Run it yourself with `python3 -m contacts.demo.server`, then open `http://127.0.0.1:8765/`. The
  page's "Import CSV" button posts the chosen file to this process' `/parse` endpoint, which calls
  `parse_google_csv()` directly — one real, tested parser, not a second hand-rolled one in JS.
  Nothing goes past 127.0.0.1, and no Claude Code session has access to this server or anything
  sent to it.

## Status

Built 2026-09-05, TDD throughout (tests against synthetic fixture data only — no real exported
file has ever been read by this session, per Joakim's explicit privacy requirement). The demo's
CSV import originally duplicated `parse_google_csv()`'s logic in hand-rolled JS that split rows on
plain commas — it would misparse any real export with a quoted field containing a comma (e.g. a
Notes column). Fixed same day by removing the duplicate JS parser entirely and adding
`demo/server.py`, a local-only server the demo now calls so there's a single parser to keep
correct. Not yet wired into any UI or into `entities`/`tag_references` — see IDENTITY_MATCHING.md's
"Contacts-import desktop fallback" section for what's still open (live-sync provider choice, actual
entity-linking step).
