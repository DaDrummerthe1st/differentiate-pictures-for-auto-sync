# Scope app photo endpoints and tags to per-user username

Second increment of `documentation/plans/deep-singing-firefly.md` (per-user private photo
storage): every `app/` (photo-viewer) endpoint — `upload`, `tree`, `file-summary`, `thumb`,
`original` — now scopes to `dpfas_media/<username>/` via the JWT's own username claim
(`app/auth.py`'s new `require_session_with_username`, fails closed on a missing claim), replacing
the old numeric-`user_id` folder and the admin source-switcher (`app_settings` table,
`GET`/`PUT /api/settings/photos-source`) entirely — removed backend-side this increment, frontend
UI removal still pending. Also retired the tags admin-bypass (admin no longer sees other members'
manual tags) per Joakim's call, matching "no cross-user access, no admin bypass" for tag metadata
too, not just photo bytes. Caught and fixed a latent cross-user leak in the same pass: the
thumbnail cache key was relative-path-only, not per-user, so two users with an identically-named
relpath could have served each other's cached thumbnail — now `THUMB_CACHE/<username>/<relpath>`.
TDD throughout, 108/108 `app/tests/` passing. `app/benchmark_detector.py` (a direct-filesystem CLI
tool, not an HTTP endpoint) updated to walk the whole `dpfas_media` tree instead of the removed
`get_active_photos_root()`.

- **Doc size**: this entry only — code-only increment, no other docs touched yet (frontend removal,
  lightbox fix, and the SCHEMA.md/GLOSSARY.md pass are separate, still-pending increments of the
  same plan).
