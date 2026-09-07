# nas/

Server-side NAS application design — the "server in some user's home" piece [VISION.md](../VISION.md)'s native-app pivot section named as starting fresh once scoped. Opened 2026-09-07, its own worktree/branch (`worktree-nas-server-design`) specifically so this session doesn't collide with the concurrently-active mobile-app session — see [../mobile/TODO.md](../mobile/TODO.md)'s own "recommended as its own session, own branch, own worktree" note, written by that session for exactly this situation.

## What the NAS is, in one paragraph

Not a backend the phone merely calls into — a full peer. The NAS runs its own PWA, reachable from any browser on the LAN (a computer, or the phone's own browser), that does the same photo triage/tagging/curation work the native Android app does, independently of whether a phone is even connected. Joakim's framing: most users will primarily work from the phone, but the same work must be possible from a computer connected to the NAS, because not every user has regular computer access — the NAS is a first-class interface, not a fallback. Phone and NAS talk to each other bidirectionally — the NAS can ask about the phone's state (on-device confidence scores, what's on the device) the same way the phone can ask about the NAS's.

## Where this sits among the four storage areas

Joakim's framing, 2026-09-07: four possible storage areas exist in a user's network — the phone app (native Android, other session/topic: [../mobile/](../mobile/README.md)), this NAS, a future DFS (torrent-style, users' own private/shared network: [../distributed-sync/](../distributed-sync/README.md)), and future bought disk space (a marketplace product: [../income/TODO.md](../income/TODO.md)). This folder designs the NAS piece. DFS and bought disk space are deliberately out of scope for this pass — both already have their own (thin) docs and stay that way here; [ARCHITECTURE.md](ARCHITECTURE.md) leaves one deliberate extension seam so plugging them in later doesn't need a schema rewrite, without designing either now. Matches [VISION.md](../VISION.md)'s existing caution that Pillar 1 isn't part of the current design phase.

## Deployment target

`192.168.1.10` — Joakim's real home server, documented in the separate `~/code/resources/hardware/` repo (not cloned into this one; see [DEPLOY.md](DEPLOY.md)). **Code here is a completely clean slate** — [../../previous-work/multi-user-web-app/](../../previous-work/README.md) (the old photo-server) is inspiration only, per Joakim's explicit instruction 2026-09-07, not a base to port from.

## Files

| File | What's there |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Tech stack, why the NAS can resume the original server-side-inference design the native pivot moved off the phone, storage layout, detector porting, the DFS/marketplace extension seam. |
| [DATA_MODEL.md](DATA_MODEL.md) | The Postgres schema new to the NAS (`photos`, `devices`, `sync_queue`, `detector_runs`, `embeddings`) — reuses [../tags/SCHEMA.md](../tags/SCHEMA.md) unchanged for everything tag-related. |
| [SYNC_CONTRACT.md](SYNC_CONTRACT.md) | The phone↔NAS interaction contract — pairing/auth, endpoints, the user-controlled sync-priority model. **Proposal, not settled** — needs the mobile session's buy-in before either side builds against it. |
| [UX_FLOWS.md](UX_FLOWS.md) | Vision-level sketch of the NAS PWA's own screens — pairing/devices, browse/triage, sync-priority flagging, storage dashboard, curation review. |
| [DEPLOY.md](DEPLOY.md) | The `.10` target, what `nas/deploy.sh` does, and why this session never runs it itself. |
| [TODO.md](TODO.md) | What's designed vs. still open. |

## Status

Design + framework scaffolding pass, opened and done 2026-09-07. No code deployed anywhere; nothing has run against the real `.10` server.
