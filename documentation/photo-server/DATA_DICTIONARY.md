# Data dictionary — photo-server

PostgreSQL, one instance, no separate search or vector store (see
[README.md](README.md)). "Now" = in scope for the Phase 0–6 roadmap in
[TODO.md](TODO.md) — **not the same as already implemented**; check
TODO.md's own phase status for what actually exists today. As of
2026-07-19 (Phase 1 done, Phase 2 not started), only `users` and
`audit_log` are real tables in the database (`server/app/db.py`'s
`ensure_schema()`) — `photos`, `photo_owners`, and `tags` are designed
but not yet created. "Reserved" = column/table exists in the schema,
not populated/used yet.

## Flagged call: `selections` is dropped, not just amended

The original build plan specced a `selections` table (per-user,
per-photo mark/download state) for Phase D. The later GUI-spec amendment
introduced `tags` with `kind = 'album'`, carrying its own per-(tag,
photo) `downloaded_at`/`download_count` and its own zip-download
endpoint. Both mechanisms solve the same problem — "which photos has
this user picked, and have they been downloaded yet" — and running both
would mean two competing sources of truth for the same fact. This
document assumes **`selections` is superseded and dropped**; tags
(`kind='album'`) is the only mark/download mechanism. This is an
inference, not something either source document said explicitly —
confirm with Joakim before building Phase 2, and revert this call if
wrong.

## users

| Column | Type | Status |
| --- | --- | --- |
| id | pk | now |
| email | unique | now |
| password_hash | argon2id | now (changed from bcrypt 2026-07-16 — see TODO.md Phase 1's architecture note) |
| role | admin / member | now |
| created_at | timestamp | now |

## photos

| Column | Type | Status |
| --- | --- | --- |
| id | pk | now |
| catalogue | text, raw folder name, never parsed (see MOCKUP.md / GUI spec §2) | now |
| filename | text | now |
| media_type | text | now |
| source_disc | text | now |
| file_hash | sha256, dedup key | now |
| file_size | bigint | now |
| width, height | int | now |
| orientation | computed | now |
| exif_datetime | timestamp, nullable — **no mtime fallback**, null means "date unknown" in the UI, expected to be common | now |
| exif_gps_lat, exif_gps_lon | numeric, nullable | now |
| user_location_tag | text | now, empty until entered |
| search_vector | generated tsvector over filename/catalogue/user_location_tag, GIN index | now |
| ingested_at | timestamp | now |

`unique(catalogue, filename)`.

## photo_owners

| Column | Status |
| --- | --- |
| photo_id, user_id | now |
| visibility | now |
| added_at | now |

A photo exists once on disk regardless of how many users can see it;
deleting a row removes only that owner's access until zero remain.

## tags (the album mechanism — also the mark/download mechanism)

| Column | Status |
| --- | --- |
| id, photo_id, user_id, tag, kind, created_at | now |
| downloaded_at, download_count | now — **per (tag, photo) pair**, not per photo |

`unique(photo_id, user_id, tag)`. `kind = 'album'` is the only value
built now (default); `kind = 'content'` is reserved for the deferred
free-text manual-tagging path (see DEFERRED.md) so the two never mix in
a person's album list.

Endpoints (kind='album' only): `GET/POST /tags`, `POST`/`DELETE
/tags/{tag}/photos/{photo_id}`, `GET /tags/{tag}/photos`, `GET
/tags/{tag}/download` (zip; default = only photos with null
`downloaded_at` for that tag, `?full=true` re-zips everything, both
update `downloaded_at`/`download_count`).

## share_links

Schema only, no endpoints (see DEFERRED.md).

| Column | Status |
| --- | --- |
| id, owner_user_id, scope_type, scope_id, token, created_at, expires_at, revoked | reserved |

## audit_log

| Column | Status |
| --- | --- |
| id, user_id, action, catalogue, filename, details (JSONB), created_at | now |

Login, mark/unmark-equivalent (tag add/remove), and download actions are
logged. Browsing itself is not. `details` must never carry raw GPS/EXIF
values into logs — ties to [POLICY.md](../policies/POLICY.md)'s
location-data rule; see also the security checklist in TODO.md.

## Tag dimensions

| Dimension | Source | When |
| --- | --- | --- |
| Catalogue | folder name | now |
| Media type | file signature | now |
| Provenance | ingestion context | now |
| Date/time | EXIF only, no mtime fallback | now |
| GPS position | EXIF | now |
| User location tag | user input | now, empty until entered |
| Orientation | computed | now |
| Full-text search | Postgres tsvector | now, demoted in UI (small, collapsed by default) |
| Album tags (`kind='album'`) | user input | now — the core browsing/selection mechanism |
| Manual content tags (`kind='content'`) | user input | schema now, endpoints fast-follow |
| Monochrome/blur | — | deferred entirely, not designed |
| Near-duplicate cluster | perceptual hash | fast-follow |
| Scan heuristic | heuristic | fast-follow |
| Content tags, face regions/identity | on-device model, phone side; pgvector server-side once it exists | DPFAS phase |
| People count | derived from face regions | DPFAS phase |
| Outcome/usage | album tags plus audit_log | now for data, used later |
| Ownership | photo_owners | now, schema only |

### Future tag schema (captured 2026-07-18, not designed/committed)

Joakim proposed a general shape for tags once the dimensions above grow
past today's album/content split - captured here for a future session,
not scoped for this project's current phase:

- `tags`: `id, name, type (folder|blur|identified_individual|...), flag
  (global — system-set, vs. private — user's own), created_at`.
- A separate reference table (not a graph DB - see below) for what a tag
  points at: a user, a pixel region (e.g. a face's bounding box,
  `[(23,466),(186,1234)]`), another tag, or a plain email address (an
  invite/"recruit to view these pictures" mechanism, not yet designed
  elsewhere).

**Relational, not graph DB** (Joakim agreed 2026-07-18, "at least for
now"): a graph database earns its cost at a node/edge count and
traversal complexity this project doesn't have (one household, later
some invited relatives - not a dense social graph). A `tags` +
`tag_references` pair, with `reference_kind` discriminating what
`reference_value` (JSONB or text) means per row, covers every case
above natively in Postgres - already this project's database, already
handling similar polymorphic/semi-structured data (see `details JSONB`
in `audit_log` above). Revisit only if real scale ever demands it, not
preemptively.
