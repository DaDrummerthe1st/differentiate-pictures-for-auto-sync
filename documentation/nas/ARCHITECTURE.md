# Architecture

## The NAS is a peer, not "the" backend

The phone talks to the NAS and the NAS talks to the phone — [SYNC_CONTRACT.md](SYNC_CONTRACT.md) is deliberately bidirectional, not a client/server hierarchy. Either side can be used standalone: the phone works with no NAS reachable, and the NAS's own PWA works with no phone ever connected (someone uploading photos from a camera SD card via a computer, say). Sync reconciles the two when both are present; neither depends on the other to function.

## Why the NAS can resume the pre-pivot server-side design

[VISION.md](../VISION.md)'s 2026-09-05 native-app pivot moved photo *inference* (quality scoring, object detection) onto the phone, and the phone's *client* off a PWA onto a native Android app — but both of those moves were specifically about a **closed OS photo library a background browser process can't reach** (see [../curation/IDENTITY_MATCHING.md](../curation/IDENTITY_MATCHING.md)'s "Reversed 2026-09-05" note). Neither constraint applies to the NAS: it's an always-on server that already owns the files it holds, and a PWA serving its UI has no OS-level background-access problem to work around. So the NAS's own architecture is, in effect, the original [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md) design (detectors → embedding index → Curator, Postgres+pgvector, browser UI) applied to itself — not superseded by the pivot, just no longer assumed to be the *only* place inference happens. **Fresh code, not ported**: [../../previous-work/multi-user-web-app/](../../previous-work/README.md) is inspiration only, per Joakim's explicit 2026-09-07 instruction — schema/library choices there are things to weigh, not things already settled.

Concretely, this means the NAS runs its own copy of the detection pipeline (quality scoring, object detection, and whatever else [../curation/DETECTORS.md](../curation/DETECTORS.md) catalogs) server-side, independent of the phone's on-device copy. Two real, independent inference sites, not one canonical one — see [SYNC_CONTRACT.md](SYNC_CONTRACT.md) for how their outputs reconcile when a photo exists on both.

## Tech stack

- **Backend**: Python (uv-managed, matching this project's existing convention), FastAPI, Docker Compose. Fresh code under `nas/backend/`.
- **Database**: Postgres 16+ with the `pgvector` extension — one instance, matching [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s existing assumption and [../tags/SCHEMA.md](../tags/SCHEMA.md)'s "relational, not graph DB" decision. Holds metadata, tags, embeddings, and sync state — never photo bytes themselves.
- **No Redis beyond the already-decided auth pattern**: [../policies/AUTHENTICATION.md](../policies/AUTHENTICATION.md) already specifies JWT access/refresh tokens backed by Redis for revocation, for human PWA logins — reused as-is here, not reinvented. No other new service (job queue, cache) is added in this pass; the sync-request queue in [SYNC_CONTRACT.md](SYNC_CONTRACT.md) is a plain Postgres table, not a new broker — keeps the resource footprint tight per [../policies/POLICY.md](../policies/POLICY.md)'s hard resource-efficiency constraint, especially since this stack is meant to also fit a future Pi-class device (see the hardware repo pointer in [DEPLOY.md](DEPLOY.md)).
- **Frontend**: a lightweight, framework-free PWA (`nas/frontend/`) — plain HTML/CSS/JS, a manifest, and a service worker. No build toolchain on the NAS side, consistent with the resource-tight policy and avoiding a second toolchain to keep current (Joakim's decision, 2026-09-07, over a Svelte/Preact alternative).

## Network exposure — LAN + WireGuard, no public hostname

Decided 2026-09-07, resolving the deploy port question: the NAS PWA and its API are reachable on the home LAN directly, and off-LAN only through the existing WireGuard tunnel (`wg0`) to `.10` — the same mechanism already set up so Joakim can SSH to `.10` from outside without exposing it to the WAN (see the hardware repo pointer in [DEPLOY.md](DEPLOY.md)). No public hostname, no public port. This is more consistent with [../policies/POLICY.md](../policies/POLICY.md)'s closed-by-default posture than reopening `photos.reuterborg.se` (the old photo-server's now-obsolete public site, which Joakim confirmed can be retired), and it sidesteps needing a Let's Encrypt certificate at all — a self-signed/local-CA cert is enough for a LAN/VPN-only service, one less exception to POLICY.md's "closed-by-default, sole exception Let's Encrypt" rule to carry. The phone's own remote sync (when off home wifi) is expected to reach the NAS the same way, likely a second WireGuard peer — not designed in detail here, flagged in [TODO.md](TODO.md).

## Storage layout

Photo bytes live directly on the ZFS `tank` pool the `.10` server already has (see [DEPLOY.md](DEPLOY.md)), addressed by content hash — this project's storage has always been content-addressed (see [GLOSSARY.md](../GLOSSARY.md)'s existing entry), so identical bytes synced from two sources (phone + a direct computer upload) collapse to one file automatically. Postgres never stores a copy of the bytes, only `photos.content_hash`, EXIF, and a relative path under `tank`.

## Extension seam for DFS / bought disk space (not built)

The one deliberate hook: a photo's byte location is modeled as `photos.storage_location` (today, always a fixed `"local-zfs"` tag pointing at the `tank` path) rather than every query assuming a local filesystem path directly. This is the only concession made toward [../distributed-sync/](../distributed-sync/README.md) (DFS) and the future paid-storage marketplace ([../income/TODO.md](../income/TODO.md)) — neither is designed here, and nothing about today's schema depends on either ever existing. Revisit once a second real storage node exists, per [../VISION.md](../VISION.md)'s existing caution against designing Pillar 1 prematurely.

## Detector porting

Concretely, "the NAS runs its own copy of the detection pipeline" means [../curation/DETECTORS.md](../curation/DETECTORS.md)'s catalog (quality trio, face/object/animal detection, scene classification, and whatever else it names) runs as NAS-side code writing `detector_runs` rows with `source='nas-server-side'` — see [DATA_MODEL.md](DATA_MODEL.md). The old `detector/` container (quality trio + YuNet face detection, built against photo-server) is archived under `previous-work/` — inspiration for which models were already found to work on this CPU-only hardware, not a base to resume; fresh code, same as everything else under `nas/`. Model choice itself isn't redecided here — [../curation/DETECTORS.md](../curation/DETECTORS.md) already researched this breadth-first and stays the authoritative catalog; this section only says where the code that runs those models now lives.

## Open tension, flagged not resolved: pilot-usage learning vs. no-telemetry

Raised by Joakim 2026-09-07, discussing sync-priority UX: he wants pilot users early and "a non-invasive way of learning how each individual is using the features" — calling it possibly the most important thing for finding this project's real USPs. That is usage analytics, which sits in direct tension with [../policies/POLICY.md](../policies/POLICY.md)'s hard "closed-by-default... no telemetry" rule. **Not designed or built here** — logged as an open question in [../policies/POLICY.md](../policies/POLICY.md)'s Open questions section; needs Joakim's explicit resolution (e.g. opt-in only, local-only aggregate the user can inspect/export herself, something else) before any usage-learning mechanism gets designed, let alone built.

## Status

Designed 2026-09-07, alongside the framework scaffolding under `nas/`. No migration has run against a real database; nothing is deployed.
