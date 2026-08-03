# TODO — distributed-sync

Nothing built yet. Captured from early notes and the initial documentation session:

- Sync between devices (general, PC-to-PC).
- Android → PC sync over local WLAN.
- Android → PC sync over WAN.
- Phone app gesture UX: swipe left = discard, right = save, down = mark, up = undo.
- On mobile devices not yet synced with the server: rename discarded files so common gallery apps don't surface them; keep a local temp database of choices and sync it once connectivity is available.
- Self-hosted NAS device spec — see [README.md](README.md) for the full vision as described so far.
- Shared/distributed file system where users can dedicate spare storage and AI compute in exchange for shared access — architecture not yet decided.
- **Mobile app platform: native vs. Flutter — undecided.** Not urgent, carried forward so it isn't lost; revisit once mobile sync work above actually starts.

**Open question**: full roadmap addendum, still pending from Joakim — don't treat README.md's vision as final. Includes the stability mechanism (README.md mentions blockchain-like, undefined) and how redundancy/uptime get verified across nodes.

**Open question, raised 2026-07-27, embeddings added as a concrete second instance 2026-08-03**: where does [tags/](../tags/README.md)'s metadata (`tags`/`entities`/`tag_references`, Postgres + pgvector per [../VISION.md](../VISION.md) Pillar 2) actually live once a photo's *bytes* are redundantly scattered across this DFS? [curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s detector/embedding-index design (2026-08-02/03) confirms this same open question extends to per-photo embeddings and nearest-neighbor search — a sharded, distributed vector index is a genuinely harder problem than single-instance pgvector, correctly out of scope for curation/'s current design (which assumes one Postgres instance, per VISION.md's single-VPS-for-now constraint) and deferred here instead, not designed in either place yet. The implicit assumption so far is that each user's own metadata stays on her own node, same as [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)'s per-server scoping — but that would make metadata a single point of failure the DFS was built specifically to avoid for the photo bytes themselves. Whether metadata needs its own redundancy mechanism, independent of file-level redundancy, is undecided. Same "named, not designed" category as the strict-share-vs-durable-storage tension, which got a paper resolution 2026-07-28 — see [OWNERSHIP.md](OWNERSHIP.md) (strict/leased/free tiers, access vs. storage-contribution as orthogonal axes) — still not built or scheduled. Revisit this metadata-placement question together once a second real node exists. [METADATA.md](METADATA.md) (2026-07-28/29) resolves the *exposure-boundary* half of this (raw tag data vs. aggregate signal, bounding-boxes-without-names) — the *network mechanism* half is the open item directly below.

**Open question, raised 2026-07-28/29, partially resolved by research 2026-07-29** (sources logged to `~/.claude/research_log.jsonl` per this project's research-log convention, not repeated here — ~25 citations spanning Kubo's own docs, IPFS forum reports, IACR ePrint papers, and arXiv): what actually carries metadata across nodes?

- **IPFS is ruled out for this project's Pi-class target, specifically** — not merely unverified. Independent reports confirm real nodes get OOM-killed under 1 GB RAM and spike to multiple GB under swarm load. Private/permissioned swarms (`swarm.key`) exist but are filed as an explicitly experimental Kubo feature. No lighter implementation found (Helia, Iroh) closes this gap for embedded devices.
- **The underlying idea (a Kademlia-style DHT, no mining) is still sound** — IPFS is one implementation of it, not the concept itself. A DFS layer, if ever built, would need either a custom lighter protocol on top of this project's own already-existing content-addressed storage, or a different existing primitive — not full IPFS.
- **PoW and PoS are both mature and well-understood, but neither actually solves this project's problem** (scoring heterogeneous storage/compute contribution honestly) — they're built to secure a ledger against a contested resource, not to price out "did this node really do the work" claims.
- **"Proof of useful work" (including tying consensus/reward to the on-device AI inference this project needs anyway) is a genuine research gap, not a working pattern to adopt.** Real academic lineage exists (Primecoin, 2013 onward), but a 2025 review of 50+ constructions found the field still "lacks practical relevance," and a 2026 empirical study of a real deployed AI-flavored coin found **zero actual inference occurring** — the verification-of-usefulness problem was gamed away entirely. Don't design against this as if it were solved.
- Mining-based approaches remain in real tension with [../policies/POLICY.md](../policies/POLICY.md)'s Pi-class resource constraint regardless of the above — this only reinforces the conclusion, doesn't add a new one.

**Marketplace idea, the business/vision rollout timeline, and the storage-contribution incentive sketch moved to [../income/TODO.md](../income/TODO.md), 2026-07-29** — business/monetization content, not this file's own technical scope. Not repeated here.

## Ownership-model correction to weigh — raised 2026-07-29, not yet resolved

Joakim's framing: "I've imagined this as a torrent-solution where even private files could be split up on different machines and only I know how to assemble them." This directly challenges [OWNERSHIP.md](OWNERSHIP.md)'s current claim that **strict**-tier content is "never replicated onto any node but the owner's own" (traded away for full privacy). Reconsider: if a file is split via secret-sharing/erasure coding and encrypted such that *only the owner ever holds a valid reassembly key*, there may be no real reason strict content can't *also* get DFS-level redundancy (shards on other people's nodes) — the privacy guarantee comes from the key never being shared, not from the bytes never leaving the owner's device. If true, this simplifies the three-tier model considerably: strict/leased/free would differ only in **who ever holds a valid key** (owner only, revocable / owner + specific others, revocably / recipient becomes a real independent co-owner), not in whether redundancy is possible at all. Needs Joakim's explicit confirmation before rewriting `OWNERSHIP.md` — flagged, not yet resolved, per this project's "argue with evidence, don't silently rewrite a committed design" norm.

## IPFS alternatives

**Researched 2026-07-29** — see [NETWORK_MECHANISM.md](NETWORK_MECHANISM.md) for the full findings (Tahoe-LAFS and other lighter alternatives to full IPFS/Kubo).

Storage-contribution incentive economics (the ROI/formula sketch) moved to [../income/TODO.md](../income/TODO.md) — business/monetization content, not this file's technical scope.
