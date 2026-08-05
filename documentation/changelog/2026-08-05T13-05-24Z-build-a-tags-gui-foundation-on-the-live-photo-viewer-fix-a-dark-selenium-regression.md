# Build a tags GUI foundation on the live photo-viewer, fix a dark Selenium regression

Built a narrowed, build-ready slice of `documentation/tags/`'s 12-category taxonomy (people/places/
objects/animals + a free-text catch-all) directly into `app/` — new SQLite `tags` table keyed by photo
path (no Postgres photo catalog exists yet), `GET/POST/PATCH/DELETE /api/tags` + `GET /api/tags/values`
autocomplete, and a lightbox UI (whole-photo tags via a new "Tagga" button, manual bounding boxes by
dragging on the image, edit/delete via chips/boxes). Every row carries a `source` column so next
session's automatic-tagging work can write `source='auto'` rows into the same table with no GUI
changes. 30 new backend tests + 5 new Selenium tests, all passing, no regressions in the existing 88 +
13.

While adding the Selenium tests, found and fixed a pre-existing regression: the Selenium harness's
readiness probe (`app/tests_selenium/conftest.py`) had been silently broken for every test, not just
these new ones, since a 2026-07-23 auth-gate commit made `GET /` redirect to a `/login` this app doesn't
serve — see `documentation/bugs/repo/fixed/2026-08-05-selenium-test-harness-readiness-probe-never-
succeeds-since-the-app-shell-auth-gate-SOLVED.md` for the full trail.

- **Doc size**: `documentation/GLOSSARY.md` +338 chars, `documentation/gui/README.md` +1379,
  `documentation/tags/SCHEMA.md` +1968, `documentation/tags/README.md` +436,
  `documentation/gui/TODO.md` +2132.
