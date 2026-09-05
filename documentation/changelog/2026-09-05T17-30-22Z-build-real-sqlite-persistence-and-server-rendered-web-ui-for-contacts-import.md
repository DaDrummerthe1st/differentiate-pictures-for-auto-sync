# Build real SQLite persistence and server-rendered web UI for contacts import

Joakim confirmed the CSV parsing fix worked against his real export, then asked for the parsed
contacts to actually be saved — this turns the throwaway demo into the real feature. Added
`contacts/db.py`: `save_contacts()`/`classify_contacts()` against `databases/app.db`'s new
`contacts`/`contact_emails` tables, implementing Joakim's dedup rule exactly (email match first,
else exact display_name, else new; a match merges the whole `raw` record plus unions emails, never
a blind overwrite) — `classify_contacts()` is the read-only dry run used to render a preview before
anything is written. 13 TDD tests cover new/update/unchanged/merge-conflict/email-union cases.

Also rebuilt the whole web surface per Joakim's explicit direction ("served from python, handled by
python... backend data crunching in Python", after live back-and-forth ruling out Node.js and
client-side JS business logic): `contacts/render.py` (pure-Python HTML — two-level collapse via
native `<details>`, no JS anywhere), `contacts/multipart.py` (a small `email`-module-based
multipart/form-data parser, since Python 3.13 dropped `cgi`, so a plain `<form>` upload needs no
JS), and `contacts/demo/` renamed to `contacts/web/` (this is production code now, not a mockup) -
`GET /` upload form → `POST /preview` (classify, no write) → `POST /save` (persist) →
`GET /contacts` (browse everything stored), every response a full server-rendered page. Verified
end-to-end via curl against the real HTTP server with synthetic data (Joakim pre-approved starting
it briefly for this) before handing back for real-export testing.

- **Doc size**: contacts/README.md 3285 -> 5455 chars (+2170).
