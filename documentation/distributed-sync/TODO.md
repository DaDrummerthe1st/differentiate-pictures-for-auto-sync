# TODO — distributed-sync

Nothing built yet. Captured from early notes and the initial documentation session:

- Sync between devices (general, PC-to-PC).
- Android → PC sync over local WLAN.
- Android → PC sync over WAN.
- Phone app gesture UX: swipe left = discard, right = save, down = mark, up = undo.
- On mobile devices not yet synced with the server: rename discarded files so common gallery apps don't surface them; keep a local temp database of choices and sync it once connectivity is available.
- Self-hosted NAS device spec — see [README.md](README.md) for the full vision as described so far.
- Shared/distributed file system where users can dedicate spare storage and AI compute in exchange for shared access — architecture not yet decided.

**Open question**: full roadmap addendum, still pending from Joakim — don't treat README.md's vision as final. Includes the stability mechanism (README.md mentions blockchain-like, undefined) and how redundancy/uptime get verified across nodes.

**Open question, raised 2026-07-27**: where does [tags/](../tags/README.md)'s metadata (`tags`/`entities`/`tag_references`, Postgres + pgvector per [../VISION.md](../VISION.md) Pillar 2) actually live once a photo's *bytes* are redundantly scattered across this DFS? The implicit assumption so far is that each user's own metadata stays on her own node, same as [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)'s per-server scoping — but that would make metadata a single point of failure the DFS was built specifically to avoid for the photo bytes themselves. Whether metadata needs its own redundancy mechanism, independent of file-level redundancy, is undecided. Same "named, not designed" category as OWNERSHIP.md's strict-share-vs-durable-storage tension — revisit together once a second real node exists.
