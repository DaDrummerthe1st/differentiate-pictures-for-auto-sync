# Record real deploy status, missing admin account fix, and open upload-visibility bug

Joakim applied this session's `docker-compose.prod.yml` change on `.10` and it's live. Along the way,
his own login failed ("Incorrect email or password") — a read-only `SELECT` on `.10`'s `users` table
showed only Elisabeth's `member` account; Joakim's own `admin` account had apparently never been
created there (he'd only used SSH/sudo directly before, never the browser login as himself). Fixed
with `scripts.create_account --role admin`, confirmed working.

After that, a real, not-yet-root-caused bug: uploading via the new "Ladda upp bilder" button doesn't
make the picture show up in the gallery. Leading unconfirmed theory: this session's own chat gave a
fallback command for switching `active_source` to `momfiles` (to benchmark against real photos before
the upload feature existed) — if that was run and never switched back, uploads (which always land in
`dpfas_media` by design) simply wouldn't be visible while `momfiles` is served, which would be the
setting working as designed, not a bug. Also flagged: `POST /api/upload`'s failure path is silent on
the frontend today, and no automated test currently asserts an uploaded photo becomes visible via
`GET /api/tree` (`test_upload.py` only checks the file lands on disk). Recorded in
`documentation/curation/TODO.md`'s "Deploy status" note as next session's starting point.

- **Doc size**: `documentation/curation/TODO.md` +1667 chars.
