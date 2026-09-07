# Phone ↔ NAS sync contract

**Proposal, not settled.** Designed from the NAS side, 2026-09-07 — this file describes what the NAS expects and exposes. It touches the phone app's own design (background sync worker, device credential storage), which belongs to [../mobile/](../mobile/README.md)'s session/topic — treat everything below as a draft the two sides need to agree on, not a committed API either can build against unilaterally. No file under `android/` or `mobile/` was touched writing this.

## Ground rule: the user decides, always

Joakim, 2026-09-07, discussing sync priority: **the user chooses what gets worked on and when, always** — presets/recommended settings are welcome, but never a demand or a silent default behavior. His example: "the user should be able to flag area/pictures/tags/album/folder xyz to be worked with next time she is on wifi or on a computer." Extends to the whole app, not just sync: any automated behavior is offered as an intuitive, adoptable option — "used because it works best... not because I control the workflow" — same spirit as [../VISION.md](../VISION.md) Pillar 2's existing "motivated tagging, not silent automation" principle, now stated for sync/priority specifically. This governs the whole design below: the sync-request queue is filled by the user's own explicit choices first, with optional presets she can turn on, tune, or ignore.

## What "confidence-driven sync" actually means here

Resolving mobile/TODO.md's terse backlog note ("NAS... requests upload of specifically the photos it's least confident about"): every photo's cheap metadata (thumbnail, EXIF, on-device confidence/quality score, detected objects) always syncs to the NAS — small, always-on, no user decision needed. The **original, full-resolution bytes** are what stays user-controlled: the NAS's sync-request queue asks the phone for full-res originals in whatever order the user has actually chosen (explicit per-album/tag/folder flags), falling back to an optional preset (e.g. "least-confident first," as a suggestion the user can enable) only where she hasn't stated a preference. Every original is still expected to eventually land on the NAS — this is a backup, not a selective cache — the user only ever controls *order*, never *whether*.

## Device pairing (new mechanism — not covered by existing auth docs)

[../policies/AUTHENTICATION.md](../policies/AUTHENTICATION.md) covers human browser logins to the NAS's PWA (argon2id + JWT access/refresh, Redis-backed revocation) — reused as-is for that case, not redesigned here. Phone↔NAS device authentication is a different problem: no human retypes a password every sync cycle. Proposed pairing flow:

1. NAS's PWA (an already-logged-in human account) generates a one-time pairing code, shown as text + QR.
2. The phone app scans/enters it, calls `POST /pairing/claim` with the code.
3. NAS issues a long-lived, per-device API key (random, argon2id-hashed at rest in a `devices` table — never stored or logged in plaintext once issued). The phone stores it in Android Keystore.
4. Every subsequent phone→NAS or NAS→phone-directed request carries the device key as a bearer token. Revocable any time from the NAS PWA's device-management screen (deletes the `devices` row; the key stops working immediately).

**Glossary term added this session**: see [../GLOSSARY.md](../GLOSSARY.md)'s new "Device pairing" entry.

## Why NAS→phone is a queue, not a live connection

Android's background-execution limits are the whole reason the app went native in the first place ([../VISION.md](../VISION.md)'s native-app pivot) — a phone-side listening socket would run into the same OS restrictions a background browser process did. So "the NAS reaches the phone" is modeled as a **durable request queue** (a Postgres table, not a new service) that the phone's own background sync worker polls, rather than the NAS opening a connection to the phone. Same effective capability (NAS can ask the phone for things), no requirement that the phone be actively listening at any instant.

## Endpoints (NAS side — draft)

- `POST /pairing/claim` — exchange a pairing code for a device API key. See above.
- `POST /sync/photos/metadata` — phone pushes batches of `{content_hash, exif, local_id, on_device_confidence, quality_score, object_tags, thumbnail}` for photos the NAS doesn't have yet. Always-on, cheap, no user decision gates this — matches the phone's existing background-sync-trigger work in [../mobile/TODO.md](../mobile/TODO.md).
- `GET /sync/queue` — phone polls for the NAS's current full-res pull requests: a list of `{content_hash, reason}`, where `reason` is one of `user-flagged` (an explicit user choice, from either device), `preset-low-confidence` (an enabled preset, never on by default), or `explicit-backup` (the eventual "get everything" tail once higher-priority items are done).
- `POST /sync/photos/original` — phone uploads the actual bytes for one `content_hash` on the queue.
- `GET /photos`, `GET /photos/{id}`, `GET /photos/{id}/thumbnail` — browse NAS-held photos/metadata; used by the NAS's own PWA and by the phone to browse photos that live on the NAS but aren't (or are no longer) on-device.
- `GET /devices/phone/status` — NAS asks (via the same queue/poll model, not a push) for a live snapshot from the phone: pending on-device confidence scores, storage used, last-sync time — feeds the storage-transparency dashboard idea in [../mobile/TODO.md](../mobile/TODO.md), NAS-side counterpart.

## Reconciliation

A `content_hash` present via both a phone sync and a direct NAS-side upload (e.g. from a camera SD card) is one row, one file — matches the project's existing content-addressed-storage pattern (see [ARCHITECTURE.md](ARCHITECTURE.md)). Each independent inference result (phone's on-device scoring vs. the NAS's own server-side detector run) is stored per-source, not overwritten — same non-destructive shape as [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s per-user tag rows, applied to per-device detector output instead.

## Status

Drafted 2026-09-07 from the NAS side only. **Needs the mobile session to review before either side implements against it** — flag this file to that session rather than building the phone-side worker from this doc alone.
