# Per-user private photo storage

Uploads must be private per-user, always, even from admin. `momfiles` folds into the same model
(Elisabeth's own folder). Retires yesterday's admin source-switcher (nothing left to switch).

- `users` gains `username`; JWT carries it.
- Every photo endpoint scopes strictly to `dpfas_media/<username>/` — no cross-user access, no
  admin bypass.
- Remove the source-switcher (endpoints, DB table, UI).
- Fix lightbox stale-image bug.
- Joakim runs the prod migration (ALTER TABLE, `mv` momfiles into `dpfas_media/elisabeth/`) — not me.
- Deferred to a separate future plan: metadata table (EXIF/filename/created_at/soft-delete/side-panel).

Will build in small, reviewable increments rather than one big batch.
