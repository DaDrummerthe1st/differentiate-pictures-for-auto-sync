# nas/ TODO

## Designed this session (2026-09-07), nothing built beyond scaffolding

- Architecture, tech stack, storage layout, detector porting, DFS/marketplace extension seam — [ARCHITECTURE.md](ARCHITECTURE.md).
- Postgres schema new to the NAS (`photos`, `devices`, `sync_queue`, `detector_runs`, `embeddings`) — [DATA_MODEL.md](DATA_MODEL.md).
- Phone↔NAS sync contract draft (pairing, endpoints, user-controlled priority) — [SYNC_CONTRACT.md](SYNC_CONTRACT.md). **Needs the mobile session's review before either side implements against it.**
- Deploy target and process shape — [DEPLOY.md](DEPLOY.md). `deploy.sh` itself blocked on Joakim's inventory pass of `.10`.

## Open, blocking further work

- **Inventory pass on `.10` not yet run** — see [DEPLOY.md](DEPLOY.md). Blocks `deploy.sh` and any real port/volume/Docker assumption.
- **Pilot-usage-learning vs. no-telemetry tension, flagged not resolved** — see [ARCHITECTURE.md](ARCHITECTURE.md)'s Open tension section and [../policies/POLICY.md](../policies/POLICY.md)'s Open questions. Needs Joakim's explicit call before any usage-analytics mechanism is designed.
- **Coordinate `SYNC_CONTRACT.md` with the mobile session** — the pairing flow and queue-polling model both assume specific phone-side behavior (Keystore-held device key, a background sync worker that polls `/sync/queue`) that session hasn't seen or agreed to yet. **2026-09-07**: Joakim will relay this himself rather than this session messaging the peer directly.

## Not designed at all yet

- Actual detector porting (code) — [ARCHITECTURE.md](ARCHITECTURE.md)'s Detector porting section says where NAS-side inference code will live and what it writes ([DATA_MODEL.md](DATA_MODEL.md)'s `detector_runs`), but no code exists; model choice itself stays [../curation/DETECTORS.md](../curation/DETECTORS.md)'s call, not redecided here.
- The NAS PWA's screens down to component/wireframe level — [UX_FLOWS.md](UX_FLOWS.md) sketches the screens vision-level, same bar as [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md); not build-ready.
- Multi-NAS (V2 rollout, each user her own box) — explicitly out of scope; this pass is one box (`.10`) only.
- DFS / bought-disk-space integration — deliberately not designed, per [ARCHITECTURE.md](ARCHITECTURE.md)'s extension-seam note.

## Status

Opened 2026-09-07.
