# Data dictionary — photo-server

PostgreSQL, one instance, no separate search or vector store (see [README.md](README.md)). "Now" = in scope for the Phase 0–6 roadmap in [TODO.md](TODO.md) — **not the same as already implemented**; check TODO.md's own phase status for what actually exists today. As of 2026-07-19 (Phase 1 done, Phase 2 not started), only `users` and `audit_log` are real tables in the database (`server/app/db.py`'s `ensure_schema()`) — `photos`, `photo_owners`, and `tags` are designed but not yet created. "Reserved" = column/table exists in the schema, not populated/used yet.

## Flagged call: `selections` is dropped, not just amended

The original build plan specced a `selections` table (per-user, per-photo mark/download state) for Phase D. The later GUI-spec amendment introduced `tags` with `kind = 'album'`, carrying its own per-(tag, photo) `downloaded_at`/`download_count` and its own zip-download endpoint. Both mechanisms solve the same problem — "which photos has this user picked, and have they been downloaded yet" — and running both would mean two competing sources of truth for the same fact. This document assumes **`selections` is superseded and dropped**; tags (`kind='album'`) is the only mark/download mechanism. This is an inference, not something either source document said explicitly — confirm with Joakim before building Phase 2, and revert this call if wrong.

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
| sharing_terms (strict / free), shared_from_owner_id | reserved — see [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md); one-server scope only, no network/node columns added at this stage |

A photo exists once on disk regardless of how many users can see it; deleting a row removes only that owner's access until zero remain. A **free** share creates a genuine, independent owner row (irrevocable); a **strict** share is a revocable viewing grant, not full ownership — see [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md) for the full model.

## tags

Reserved/now — full schema (columns, `category`/`visibility`, endpoints, and how
this relates to the taxonomy's other tables) moved to
[../tags/SCHEMA.md](../tags/SCHEMA.md), the tag system's authoritative home. The
`kind='album'` mechanism described there is what's actually built and live today.

## share_links

Schema only, no endpoints (see DEFERRED.md).

| Column | Status |
| --- | --- |
| id, owner_user_id, scope_type, scope_id, token, created_at, expires_at, revoked | reserved |

## pending_shares

Reserved, no endpoints — backs the email-invite share mechanism ([../upload-and-share/SHARING.md](../upload-and-share/SHARING.md)): a share aimed at an email with no DPFAS account yet, resolved into a real `photo_owners` row automatically on that email's first login.

| Column | Status |
| --- | --- |
| id, target_email, scope_type (photo/tag), scope_id, sharing_terms, invited_by_user_id, created_at, resolved_at | reserved |

## tag_endorsements

Reserved, no endpoints — full schema moved to [../tags/SCHEMA.md](../tags/SCHEMA.md).

## blocklist_hashes

Reserved, no endpoints — admin-only moderation override, supersedes ownership/sharing terms entirely for illegal/abusive content ([../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)'s Moderation section). Perceptual hash (PDQ), not `photos.file_hash` (sha256 exact-match) — catches re-encoded/resized copies of flagged content.

| Column | Status |
| --- | --- |
| id, perceptual_hash, algorithm, reason, added_by_admin_id, created_at | reserved |

## events

Reserved, no endpoints — one row per party/wedding/funeral-style event ([../upload-and-share/EVENTS.md](../upload-and-share/EVENTS.md)). `tag_id` is the event's underlying `kind='album'` tag, auto-applied to every photo uploaded through the event's QR token. `event_account_user_id` is a dedicated `users` row created with the event — free-for-all uploads' `photo_owners.user_id` is this account, never the anonymous guest and never a claimable pending record (resolved 2026-07-26); `host_user_id` is the human who administers the event and is a separate row from it.

| Column | Status |
| --- | --- |
| id, host_user_id, event_account_user_id, name, tag_id, qr_token, upload_access (free_for_all / pre_approved / register_then_approve), visibility_scope (all / curated), tv_display (bool), created_at | reserved |

## audit_log

| Column | Status |
| --- | --- |
| id, user_id, action, catalogue, filename, details (JSONB), created_at | now |

Login, mark/unmark-equivalent (tag add/remove), and download actions are logged. Browsing itself is not. `details` must never carry raw GPS/EXIF values into logs — ties to [POLICY.md](../policies/POLICY.md)'s location-data rule; see also the security checklist in TODO.md.

## Tag dimensions

Superseded by [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s 12-category taxonomy —
that file is now the source of truth for what a tag can represent and how the
categories relate; the old draft "Future tag schema" sketch this section used to
carry is fully absorbed into [../tags/SCHEMA.md](../tags/SCHEMA.md).
