# Upload flow

## What replaces `catalogue` for a web upload

Disc-ripping ingestion ([../photo-server/TODO.md](../photo-server/TODO.md) Phase 3) sets `catalogue` from the source folder name. A browser file picker exposes no such folder. Resolution: **user-named batch at upload time**, stored as an auto-created tag (same mechanism as today's `kind='album'` tags — no schema split):

```
Upload dialog:
┌──────────────────────────────┐
│ Name this batch (optional):  │
│ [ Summer 2019__________ ]    │
│ [ Choose files… ]            │
│            [ Upload ]        │
└──────────────────────────────┘
Empty name -> catalogue = "web-upload-{user}-{timestamp}"
```

This isn't cosmetic: `catalogue` is half of the ingestion dedup key (`unique(catalogue, filename)`, see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)) and the only "these happened together" signal the system gets for free, before any manual tagging — directly serving the tagging-density goal in [OWNERSHIP.md](OWNERSHIP.md) (a whole batch already carries one shared tag before a human tags a single photo). This batch tag is concretely the **origin** category in [../tags/TAXONOMY.md](../tags/TAXONOMY.md).

## Event uploads

An event's QR code encodes a token that resolves to a specific event's tag (see [EVENTS.md](EVENTS.md)). Every photo uploaded through that token gets that event's tag applied automatically as its origin/first tag — the batch-naming step above still happens, but the event tag is pre-set by the host, not typed by the uploader.

## Storage layout

Two separate concerns, deliberately decoupled:

- **Physical bytes on disk**: content-addressed, hash-prefix-sharded — `<sha256-prefix>/<sha256-prefix>/<sha256>.<ext>`. Nobody browses this directly; it exists purely to avoid one directory holding an unbounded number of entries (a real filesystem limit) while getting free deduplication — a shared photo is one file with N `photo_owners` rows, never N copies. Replaces the current single-account `/tank/momfiles` mount (see [../photo-server/DEFERRED.md](../photo-server/DEFERRED.md)'s "single consolidated media root" entry, and `PHOTOS_HOST_PATH` in [../photo-server/DEPLOYMENT.md](../photo-server/DEPLOYMENT.md)) with one shared root across every account, disregarding ownership entirely at the filesystem level — the app layer, not the mount point, is what enforces who can see what.
- **Human-facing organization**: entirely in the database via tags — strictly more expressive than folders, since one photo can carry multiple tags at once (an event tag, a person tag, a location tag) where a folder forces exactly one parent.

**Not touched this session**: actually migrating the live server's mount point off `/tank/momfiles` is a real deployment change (`docker-compose.prod.yml`, `PHOTOS_HOST_PATH`, `HARDWARE.md`) — high-blast-radius per [../../CLAUDE.md](../../CLAUDE.md), handed to Joakim as copyable commands when this build phase actually starts, not run directly and not attempted in this design-only session.

## Status

Designed 2026-07-26 (branch `upload-and-share`). No code, no deployment change. See [TODO.md](TODO.md).
