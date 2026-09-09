# Data model

Postgres, one instance, matching [../tags/SCHEMA.md](../tags/SCHEMA.md)'s "relational, not graph DB" decision and [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s pgvector-in-the-same-instance choice — both reused as-is here, not redesigned. `tags`/`entities`/`tag_references`/`tag_endorsements` are unchanged from [../tags/SCHEMA.md](../tags/SCHEMA.md); this file only adds the tables that are new to the NAS. **Fresh schema, not resumed from [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)** — per [VISION.md](../VISION.md)'s explicit "doesn't resume from photo-server's old schema" note and Joakim's 2026-09-07 clean-slate instruction; that file's `photos`/`users`/`photo_owners` are reference for what's already been thought through, not a base to inherit column-for-column.

## `photos`

| Column | Meaning |
| --- | --- |
| id | pk |
| content_hash | sha256, dedup key, `unique` — matches this project's existing content-addressed-storage pattern ([GLOSSARY.md](../GLOSSARY.md)) |
| storage_location | text, default `'local-zfs'` — the one DFS/marketplace extension seam, see [ARCHITECTURE.md](ARCHITECTURE.md) |
| relative_path | path under `storage_location` (today, under `/tank`) |
| thumbnail_path | nullable — set once a thumbnail exists, independent of whether the full original does |
| full_bytes_present | bool — **the metadata-vs-original distinction [SYNC_CONTRACT.md](SYNC_CONTRACT.md) depends on**: a row can exist (thumbnail + metadata synced) with this `false` until the original is actually pulled |
| file_size, width, height | — |
| exif_datetime | nullable, no mtime fallback (matches [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)'s existing convention) |
| exif_gps_lat, exif_gps_lon | nullable — sensitive by default, never transmitted beyond what a feature strictly needs, per [../policies/POLICY.md](../policies/POLICY.md) |
| ingest_source | `phone-sync` \| `direct-upload` — direct-upload covers a computer/SD-card upload via the NAS's own PWA |
| ingested_at | — |

`unique(content_hash)`.

## `devices`

One row per **phone**, not per PWA browser session (a human browser login uses the JWT flow in [../policies/AUTHENTICATION.md](../policies/AUTHENTICATION.md) instead — no `devices` row). See [SYNC_CONTRACT.md](SYNC_CONTRACT.md)'s pairing flow.

| Column | Meaning |
| --- | --- |
| id | pk |
| device_name | user-assigned at pairing time, e.g. "Joakim's phone" |
| api_key_hash | argon2id — the pairing-issued device credential, never stored in plaintext |
| paired_at, last_seen_at | — |
| revoked_at | nullable — set when a human revokes the device from the PWA's device list; a non-null value fails every subsequent request from that key |

## `sync_queue`

The NAS→phone request queue [SYNC_CONTRACT.md](SYNC_CONTRACT.md) describes — a plain table, not a new broker service (per [ARCHITECTURE.md](ARCHITECTURE.md)'s resource-tightness note).

| Column | Meaning |
| --- | --- |
| id | pk |
| content_hash | which photo's original is being requested (may not have a `photos` row yet if only the phone knows about it so far) |
| device_id | FK → `devices.id` — which phone this request targets |
| reason | `user-flagged` (an explicit choice, from either device) \| `preset-low-confidence` (an enabled preset, never on by default) \| `preset-full-backup` (an enabled "back up everything in this album/tag/folder" preset, also never on by default — **renamed from `explicit-backup` 2026-09-09**, see [SYNC_CONTRACT.md](SYNC_CONTRACT.md), since the old name/description implied an automatic eventual-everything fallback that contradicted the user-always-decides rule) |
| priority_rank | nullable int — orders `user-flagged` rows against each other; presets sort after all user-flagged rows regardless of their own rank |
| requested_at, fulfilled_at | fulfilled_at nullable until the phone actually uploads the bytes |

## `detector_runs`

Append-only, never overwritten — same log-then-recompute shape [../mobile/TODO.md](../mobile/TODO.md) already chose for the phone's own on-device events table, and the same pattern this project's existing `audit_log` table uses. **Two independent inference sites** ([ARCHITECTURE.md](ARCHITECTURE.md)) means the same photo can carry rows from both — neither overwrites the other; the Curator layer ([../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)) reads across both when reasoning about a photo.

| Column | Meaning |
| --- | --- |
| id | pk |
| photo_id | FK → `photos.id` |
| source | `phone-on-device` \| `nas-server-side` |
| detector_name | e.g. `quality`, `objects`, `scene` — see [../curation/DETECTORS.md](../curation/DETECTORS.md)'s catalog |
| output | JSONB — matches this project's existing polymorphic-column precedent (`entities.attributes`, `tag_references.reference_value` in [../tags/SCHEMA.md](../tags/SCHEMA.md)) |
| confidence | nullable numeric — what [SYNC_CONTRACT.md](SYNC_CONTRACT.md)'s `preset-low-confidence` reason sorts on |
| run_at | — |

No `unique` constraint — a later run for the same `(photo_id, source, detector_name)` is a new row, not an update; "current" value is always "most recent `run_at`," computed at read time.

## `embeddings`

| Column | Meaning |
| --- | --- |
| photo_id | FK → `photos.id` |
| source | same two-site discriminator as `detector_runs` — the phone's on-device embedding model and the NAS's heavier server-side one are expected to differ in practice |
| vector | pgvector column, per [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s existing design |
| model_name, model_version | — |
| computed_at | — |

`unique(photo_id, source)` — one current embedding per photo per source (unlike `detector_runs`, an embedding is naturally superseded rather than accumulated; nearest-neighbor search needs exactly one live vector per source to query against).

## What's unchanged, reused as-is

`tags`, `entities`, `tag_references`, `tag_endorsements` — [../tags/SCHEMA.md](../tags/SCHEMA.md), joining against this file's `photos.id` instead of the old photo-server's. No redesign needed; that schema was never tied to photo-server's specific `photos` columns beyond the FK itself.

## Status

Designed 2026-09-07. No migration written, nothing created in a real database.
