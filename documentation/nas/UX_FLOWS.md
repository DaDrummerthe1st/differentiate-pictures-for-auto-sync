# NAS PWA — UX flows

Vision-level sketch of the NAS's own screens, same bar as [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md) — not build-ready spec, write that level of detail when a build phase actually picks this up. Grounded in [ARCHITECTURE.md](ARCHITECTURE.md)/[SYNC_CONTRACT.md](SYNC_CONTRACT.md)/[DATA_MODEL.md](DATA_MODEL.md); nothing here contradicts those, this file is their screen-level shape.

## Why this needs its own screens, not just a smaller copy of the phone's

The NAS PWA does the same triage/tagging work the phone does ([README.md](README.md)) but for a different primary user situation: someone at a computer, likely reviewing a larger backlog at once (a full album import, not a single day's captures) rather than a quick phone-in-hand session. Layout can assume a bigger screen and a mouse/keyboard; the underlying data/actions are identical.

## Device pairing / management

The entry point for [SYNC_CONTRACT.md](SYNC_CONTRACT.md)'s pairing flow: an already-logged-in human generates a pairing code/QR, shown large enough to scan from across a desk. A separate "Devices" screen lists every paired phone (`device_name`, `last_seen_at`) with a one-tap revoke per row — directly against `devices.revoked_at` in [DATA_MODEL.md](DATA_MODEL.md).

## Photo browse / triage

Mirrors the phone's own grid + fullscreen view ([../mobile/README.md](../mobile/README.md)'s built contact-sheet grid and swipeable fullscreen), so a user who's used one recognizes the other immediately. Photos with `full_bytes_present=false` (metadata/thumbnail synced, original not yet pulled — [DATA_MODEL.md](DATA_MODEL.md)) still show and are still taggable — a thumbnail is enough to triage by, the pull queue below is about the original bytes, not about whether the photo is usable in the UI yet.

## Sync-priority flagging — the "user decides" screen

Directly implements [SYNC_CONTRACT.md](SYNC_CONTRACT.md)'s ground rule. From any album/tag/folder view, a "work on this next" action adds a `user-flagged` row to `sync_queue` — no separate settings page required for the common case, the flag lives right where the user is already looking at the photos. A separate, clearly-optional settings panel lists available presets (starting with "least-confident first") the user may enable, each explained in plain language before she turns it on — never on by default, matching [../VISION.md](../VISION.md) Pillar 2's existing "motivated tagging, not silent automation" principle, now applied to sync ordering too.

## Storage-transparency dashboard

The NAS-side counterpart to [../mobile/TODO.md](../mobile/TODO.md)'s backlog item — and arguably belongs here first, since the NAS is the one node positioned to aggregate the full picture: total storage per photo across device/NAS/(future DFS/paid tiers), queried via `GET /devices/phone/status` ([SYNC_CONTRACT.md](SYNC_CONTRACT.md)) for the phone's own live number plus the NAS's own `photos`/`storage_location` totals. Plain numbers, no obscuring — same reasoning [../mobile/TODO.md](../mobile/TODO.md) already gave for why this matters to deletion-focused curation.

## Curation review

Where [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s Curator layer actually talks to the user — a suggestion ("these look blurry"), grounded in real `detector_runs` values, that the user confirms or declines, never applied silently. Not redesigned here; this screen is that design's NAS-side home, nothing about it changes for running on the NAS instead of a hypothetical single VPS.

## Status

Sketched 2026-09-07. No wireframe, no component-level spec.
