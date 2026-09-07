# nas/ TODO

## Designed this session (2026-09-07), nothing built beyond scaffolding

- Architecture, tech stack, storage layout, DFS/marketplace extension seam — [ARCHITECTURE.md](ARCHITECTURE.md).
- Phone↔NAS sync contract draft (pairing, endpoints, user-controlled priority) — [SYNC_CONTRACT.md](SYNC_CONTRACT.md). **Needs the mobile session's review before either side implements against it.**
- Deploy target and process shape — [DEPLOY.md](DEPLOY.md). `deploy.sh` itself blocked on Joakim's inventory pass of `.10`.

## Open, blocking further work

- **Inventory pass on `.10` not yet run** — see [DEPLOY.md](DEPLOY.md). Blocks `deploy.sh` and any real port/volume/Docker assumption.
- **Pilot-usage-learning vs. no-telemetry tension, flagged not resolved** — see [ARCHITECTURE.md](ARCHITECTURE.md)'s Open tension section and [../policies/POLICY.md](../policies/POLICY.md)'s Open questions. Needs Joakim's explicit call before any usage-analytics mechanism is designed.
- **Coordinate `SYNC_CONTRACT.md` with the mobile session** — the pairing flow and queue-polling model both assume specific phone-side behavior (Keystore-held device key, a background sync worker that polls `/sync/queue`) that session hasn't seen or agreed to yet.

## Not designed at all yet

- Detector porting onto the NAS (quality scoring, object detection) — [ARCHITECTURE.md](ARCHITECTURE.md) states the NAS runs its own copy, per [../curation/DETECTORS.md](../curation/DETECTORS.md), but no actual porting has started.
- The NAS PWA's screens/UX beyond "does the same triage work as the phone" — no wireframe, no flow doc yet.
- Multi-NAS (V2 rollout, each user her own box) — explicitly out of scope; this pass is one box (`.10`) only.
- DFS / bought-disk-space integration — deliberately not designed, per [ARCHITECTURE.md](ARCHITECTURE.md)'s extension-seam note.

## Status

Opened 2026-09-07.
