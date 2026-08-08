# Add POST /api/upload so any user can add pictures into dpfas_media

Follow-up to this session's admin photo-source setting: the original plan assumed Joakim would
populate `/tank/dpfas_media` by hand over SSH. Real workflow instead, worked out live with Joakim:
`sshfs`-mount `/tank` onto his laptop, then a real "Ladda upp bilder" button in the gallery UI drives
a standard browser file picker into that mount and uploads over ordinary `multipart/form-data`.

New `POST /api/upload` (`app/main.py`) — any logged-in user, not admin-gated; size-capped
(`MAX_PHOTO_UPLOAD_BYTES`, same guard shape as `detector/main.py`'s existing one); picture-extension
only; content-hashed filename (SHA-256 of the bytes, never the client's original name), stored at
`dpfas_media/<user_id>/<hash>.<ext>`. Always writes to `dpfas_media` by name (`UPLOAD_SOURCE_NAME`),
never to whatever `get_active_photos_root()` currently resolves to — an explicit, tested guard
against an uploaded file ever landing in `momfiles` if an admin has switched the active source.
`docker-compose.prod.yml`'s `dpfas_media` mount dropped `:ro` accordingly; `momfiles` stays
read-only.

Full local suite green (133 tests, up from 126, including new `app/tests/test_upload.py`) plus a
second real local `docker compose up -d` smoke test: uploaded a real JPEG over HTTP as the real admin
account, confirmed it landed at the hashed path (not the original filename) and appeared correctly in
`/api/tree`, confirmed a non-picture extension and an unauthenticated request are both rejected.

While wiring the new admin photo-source read into `/thumb`'s request path, found and fixed a real,
pre-existing race: `app/main.py`'s single shared `sqlite3.Connection` (`check_same_thread=False`) was
never synchronized across FastAPI's threadpool — `test_thumb_concurrency.py`'s two-simultaneous-
requests test started flaking with a corrupted read once a second concurrent DB touch landed on that
same path, alongside the request-logging middleware's already-existing unsynchronized write. Fixed
with a single `threading.Lock` around every request-time `db.execute`/`db.commit` call site (12
functions) — see `documentation/bugs/repo/fixed/2026-08-08-shared-sqlite3-connection-unsynchronized-
across-concurrent-request-threads-SOLVED.md` for the full investigation trail. Verified with 15
consecutive clean runs of the previously-flaky test.

- **Doc size**: `documentation/curation/TODO.md` +2482 chars, `documentation/plans/tingly-humming-pudding.md`
  +858 chars, `documentation/photo-server/DEPLOYMENT.md` +219 chars, `documentation/GLOSSARY.md` +403
  chars.
