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

**Open question, raised 2026-07-27**: where does [tags/](../tags/README.md)'s metadata (`tags`/`entities`/`tag_references`, Postgres + pgvector per [../VISION.md](../VISION.md) Pillar 2) actually live once a photo's *bytes* are redundantly scattered across this DFS? The implicit assumption so far is that each user's own metadata stays on her own node, same as [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)'s per-server scoping — but that would make metadata a single point of failure the DFS was built specifically to avoid for the photo bytes themselves. Whether metadata needs its own redundancy mechanism, independent of file-level redundancy, is undecided. Same "named, not designed" category as the strict-share-vs-durable-storage tension, which got a paper resolution 2026-07-28 — see [OWNERSHIP.md](OWNERSHIP.md) (strict/leased/free tiers, access vs. storage-contribution as orthogonal axes) — still not built or scheduled. Revisit this metadata-placement question together once a second real node exists. [METADATA.md](METADATA.md) (2026-07-28/29) resolves the *exposure-boundary* half of this (raw tag data vs. aggregate signal, bounding-boxes-without-names) — the *network mechanism* half is the open item directly below.

**Open question, raised 2026-07-28/29**: what actually carries metadata across nodes — a Kademlia-style DHT (no mining, matches the "torrent-network style" framing above and this project's existing content-addressed storage), a blockchain-based ledger (and if so, mining vs. proof-of-stake vs. the much less mature "proof of useful work" — e.g. tying consensus/reward to the on-device AI inference this project needs anyway), or something else? Mining-based approaches are in real tension with [../policies/POLICY.md](../policies/POLICY.md)'s Pi-class resource constraint. Whether IPFS specifically (an existing, open-source Kademlia+content-addressing implementation) is viable on target hardware is unverified. Real research needed before any commitment — don't treat anything above as decided.

**Open idea, raised 2026-07-28/29, not designed**: letting users sell photos through the network (a marketplace layer), rather than only strict/leased/free (free/cost). Would introduce real payment/regulatory surface (a lawyer question, same category as the event-mode legal-reporting flag in [../policies/POLICY.md](../policies/POLICY.md)) and likely a new price/for-sale attribute layered onto the existing ownership tiers rather than a redesign of them — provenance/rights-verification (proving a seller actually owns what she's offering) reuses the entity/ownership chain already being built. Not researched, not scoped — flagged so it isn't lost.
