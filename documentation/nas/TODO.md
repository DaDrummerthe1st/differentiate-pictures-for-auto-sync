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

- **Phone's off-LAN sync path — direction confirmed 2026-09-07, not designed in detail**: WireGuard is the answer for the phone too, same as for a remote PWA browser — a second WireGuard peer alongside the existing Lenovo-workstation one, per [NETWORK.md](NETWORK.md)'s topology diagram. Not designed beyond that: peer provisioning at pairing time, how the phone's WireGuard client is configured/stored, whether it piggybacks on [SYNC_CONTRACT.md](SYNC_CONTRACT.md)'s device-pairing flow or is separate. Needs the mobile session's input, since the phone-side half is its territory.

## Security follow-up on `.10`, raised 2026-09-07 — unrelated to NAS design, surfaced by the inventory pass

- **`auth` container crash-looping** — root cause unknown, diagnostic command handed to Joakim (`docker logs differentiate-pictures-for-auto-sync-auth-1`). Likely moot once the retirement below happens, but check the logs first rather than assuming — could be relevant to the "has anyone accessed this box" question next to it.
- **Security/access audit requested** — who's logged in, login history, failed logins, full listening-port picture, and specifically whether **"buzzkit"** (one of Joakim's other, unrelated projects) is somehow running on `.10` — he noticed it "active and operational" while pasting inventory output, unconfirmed whether that was actually observed on `.10` itself or elsewhere. Diagnostic commands handed to Joakim; **results not yet seen by this session** — pick this up first thing next session if Joakim has output by then.
- **Retire the old `photos.reuterborg.se` stack** — confirmed obsolete, command already in [DEPLOY.md](DEPLOY.md) ("Retiring the old photo-server stack" section). Closes `80`/`443` and removes the crash-looping container as a side effect. Joakim's own action, not yet run as of session close.
- **Port hardening** — re-run `sudo ss -tlnp` after the retirement above to confirm `80`/`443` actually closed; separately, whether `.10`'s SSH (`22`) is reachable from the WAN depends on the EdgeRouter's own port-forward table (a separate device, not inspectable from `.10`'s own commands) — the hardware repo's network doc (last verified 2026-08-07) says only `80`/`443` were forwarded, worth Joakim reconfirming live on the router directly rather than trusting a dated doc.

## Not designed at all yet

- Actual detector porting (code) — [ARCHITECTURE.md](ARCHITECTURE.md)'s Detector porting section says where NAS-side inference code will live and what it writes ([DATA_MODEL.md](DATA_MODEL.md)'s `detector_runs`), but no code exists; model choice itself stays [../curation/DETECTORS.md](../curation/DETECTORS.md)'s call, not redecided here.
- The NAS PWA's screens down to component/wireframe level — [UX_FLOWS.md](UX_FLOWS.md) sketches the screens vision-level, same bar as [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md); not build-ready.
- Multi-NAS (V2 rollout, each user her own box) — explicitly out of scope; this pass is one box (`.10`) only.
- DFS / bought-disk-space integration — deliberately not designed, per [ARCHITECTURE.md](ARCHITECTURE.md)'s extension-seam note.

## Status

Opened 2026-09-07.
