# previous-work/

Everything under here is disregarded as code — reference and inspiration only. Nothing in
this tree is built on top of, imported from, or deployed; none of it runs, and no test suite
gates commits against it anymore (see [../.githooks/pre-commit](../.githooks/pre-commit)).

Created 2026-09-05 when the project pivoted from a phone-viewable PWA to a native Android
app (full reasoning: [../documentation/VISION.md](../documentation/VISION.md)'s 2026-09-05
note, [../documentation/plans/shimmering-wondering-swing.md](../documentation/plans/shimmering-wondering-swing.md)).
Joakim's framing: this is a clean slate on `master`, not a deletion — every previous
implementation stays available as design reference, divided below by sub-project, but no
specific past design decision (schema, architecture, library pick) carries forward as
already-settled. What *does* still stand, unchanged by this pivot: the long-term goal itself
— a fully FOSS, complete-data-ownership system, each user running on her own hardware while
optionally lending spare capacity to others on the network (Pillar 1,
[../documentation/distributed-sync/README.md](../documentation/distributed-sync/README.md)).
Ask before assuming any specific past choice still applies; don't re-derive the goal itself.

- [`pictures-pipeline/`](pictures-pipeline/README.md) — the local photo-differentiation
  library (EXIF, blur/exposure/saturation quality scoring, NanoDet-Plus object detection,
  a SQLite metadata register, a browser-based findings viewer). Formerly `modules/`.
- [`contacts-import/`](contacts-import/README.md) — the contacts CSV/vCard import and
  matching library, for name-suggestion during face-labeling. Formerly `contacts/`.
- [`multi-user-web-app/`](multi-user-web-app/README.md) — the earlier Postgres/FastAPI/
  Redis/Caddy multi-user photo server, already disregarded once before (as top-level
  `archive/`, 2026-09-04) and folded in here for one consistent location.
- [`databases-schema.sql`](databases-schema.sql) — schema-only snapshot (no rows) of the
  real, gitignored `databases/app.db` these sub-projects wrote to. `databases/` itself keeps
  holding real personal photo/contact data and stays entirely untracked; this is the one
  derived, non-personal artifact worth tracking, so a later session can see the shape without
  needing local access to real data.

## Why archive rather than delete

Per this repo's self-sufficiency rule ([../documentation/policies/WORKFLOW.md](../documentation/policies/WORKFLOW.md)):
a future session — human or AI — should be able to see what was actually built and tried,
not just read about it secondhand in a doc. Code here is the primary source for that; the
`documentation/` topic folders these sub-projects fed (`data-modeling/`, `curation/`,
`photo-server/`, `tags/`, etc.) carry dated "superseded" notes pointing back here rather than
repeating the design narrative.
