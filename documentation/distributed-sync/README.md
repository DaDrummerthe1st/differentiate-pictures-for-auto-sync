# distributed-sync/

Future work: getting pictures/movies off a single machine and onto a system the user owns and controls, without relying on a quota-limited cloud provider. Nothing here is built yet — see [TODO.md](TODO.md).

## Vision (high-level, not a committed design)

Each user runs their own device at home as a NAS — open-source and hardware-agnostic (anything from a Raspberry Pi up), acting as a small router (two network interfaces) plus a file system, reachable from the internet. Users can optionally dedicate spare storage and compute to a shared distributed file system (torrent-network style), gaining access to some shared cloud storage and AI compute in return — similar in spirit to volunteer-computing projects like SETI@home, but for storage/AI resourcing instead of signal analysis. Each user's own files stay encrypted regardless of who else's hardware is holding a redundant copy. Some blockchain-like mechanism is intended for network stability (verifying redundancy/uptime across nodes, most likely) — mechanism undefined, flagged as an open question below, not a design. The bottom line is autonomy: no single point of dependency on a third-party quota.

See [../VISION.md](../VISION.md) for how this fits alongside the other three long-term pillars (metadata/curation, presentation/sharing, multi-angle reconstruction) — this file stays scoped to the DFS piece only.

Not yet a committed design — see [TODO.md](TODO.md)'s open question for what's still unresolved.

[OWNERSHIP.md](OWNERSHIP.md) — paper-stage ownership tiers (strict/leased/free) once a second real node exists, resolving the strict-revocability-vs-durable-storage tension named in [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md).

[METADATA.md](METADATA.md) — where tag/entity metadata lives once photo bytes are distributed: raw tag data vs. aggregate/derived signal as separate exposure classes, bounding-boxes-without-names, and a private cross-network face-matching sketch (fully resolved 2026-07-29 — no published index needed at any scale).

[NETWORK_MECHANISM.md](NETWORK_MECHANISM.md) — IPFS alternatives researched 2026-07-29: Tahoe-LAFS and Garage as the two real candidates, why MinIO is now ruled out, and what's still unverified.

[HARDWARE.md](HARDWARE.md) — the device this eventually ships on, neither generation deployed yet: v1 (RPi3-class, nearer-term) vs. a speculative v2 (custom PCB, GPU-capable, hot-swappable SSD, modular incl. 5G modem), plus market precedent, the small-footprint/design-impression requirement, and the end-goal user-hardware-plus-central-server architecture — captured 2026-08-06/07. What's actually running today is the limited prototype documented in the `hardware` repo's `server/192.168.1.10/`, not this.

## Relevant external tools

Not adopted yet.

| Project | Site | Purpose |
| --- | --- | --- |
| SyncThing | https://syncthing.net/ | Continuous sync between units — lightweight in typical use, but solves a different problem (device-to-device sync, not redundancy/erasure coding). See [NETWORK_MECHANISM.md](NETWORK_MECHANISM.md). |
| rClone | https://blog.rymcg.tech/blog/linux/rclone_sync/ | Auto-sync of files via bash |
| IPFS (Kubo) | https://github.com/ipfs/kubo | Kademlia DHT + content-addressing implementation — **researched and ruled out 2026-07-29** for this project's Pi-class target. The underlying DHT concept still stands; this specific implementation doesn't fit. See [NETWORK_MECHANISM.md](NETWORK_MECHANISM.md). |
| Tahoe-LAFS | https://tahoe-lafs.org/ | **Researched 2026-07-29, leading candidate.** Encrypts then erasure-codes files across storage servers — only the key-holder can reconstruct. Storage-server role runs on ~64MB RAM; real Raspberry Pi deployments confirmed. See [NETWORK_MECHANISM.md](NETWORK_MECHANISM.md). |
| Garage | https://garagehq.deuxfleurs.fr/ | **Researched 2026-07-29, leading candidate.** Single-binary Rust S3-compatible store explicitly built for geo-distributed Raspberry-Pi-class nodes over ordinary internet (200ms latency tolerance) — closest match to this project's actual deployment shape. See [NETWORK_MECHANISM.md](NETWORK_MECHANISM.md). |
| SeaweedFS | https://github.com/seaweedfs/seaweedfs | Checked 2026-07-29 — lighter than MinIO, supports erasure coding, but volume servers reportedly want 2-4GB RAM, more than a Pi 3 has. Second-tier candidate. |
| MinIO | — | **Ruled out 2026-07-29** — ceased development, community edition archived April 2026, known security bugs, explicitly discouraged by current sources. |
| Filecoin | https://filecoin.io/ | Paid-storage marketplace precedent (on-chain escrowed deals) — prices storage capacity over time, not content licensing. See [../income/TODO.md](../income/TODO.md)'s marketplace-idea note. |
| Storj | https://www.storj.io/ | Paid-storage marketplace precedent ("satellite" coordination service, token or fiat payout) — same limitation as Filecoin for this project's purposes. |
