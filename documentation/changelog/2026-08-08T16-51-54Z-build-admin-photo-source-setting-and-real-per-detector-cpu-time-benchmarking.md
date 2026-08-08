# Build admin photo-source setting and real per-detector CPU-time benchmarking

Implemented `documentation/plans/tingly-humming-pudding.md` Parts A and B, deferred from the prior
session for token-saving reasons. Part A: `app_settings` singleton-row table, `get_active_photos_root()`
(replaces the old module-level `PHOTOS_ROOT`, used by every current endpoint), admin-only
`GET`/`PUT /api/settings/photos-source`, and an "Installningar" panel in the gallery UI, plus the
matching `docker-compose.prod.yml`/`docker-compose.yml` mount changes. Part B: `detector/main.py`'s
`/detect` gained an opt-in `include_timing` query param reporting real per-detector `resource.getrusage`
CPU time, and a new `app/benchmark_detector.py` walks the active source and logs batch summaries.
**Real, confirmed correction to the saved plan**: momfiles ended up mounted and selectable too
(not excluded, as the plan said) — every current `PHOTOS_ROOT` use also covers the live gallery
Elisabeth depends on, so the plan as written would have broken her browsing with no way back the
moment the compose change is applied on `.10`; corrected via AskUserQuestion before writing code.
Full local suite green (126 tests) plus a real local `docker compose up -d` smoke test — logged in as
the real admin account, confirmed the setting and a real source switch end to end, and ran
`app/benchmark_detector.py` against two real photos for real (non-`.10`) numbers. Also rebuilt a
locally stale `auth` image mid-smoke-test (predated the JWT role claim). Not done: the actual `.10`
deploy (Joakim's own action per POLICY.md).

- **Doc size**: `documentation/curation/TODO.md` +3718 chars, `documentation/tags/SCHEMA.md` +1169
  chars, `documentation/GLOSSARY.md` +1714 chars.
