# Network mechanism alternatives to IPFS — researched 2026-07-29

Scope: Pillar 1 per [../VISION.md](../VISION.md)'s reaffirmed scope, paper only — nothing here is built or committed. Follows up [TODO.md](TODO.md)'s 2026-07-29 finding that IPFS/Kubo itself is ruled out for this project's Pi-class hardware target (Kubo recommends 6 GB RAM, ~6x a Raspberry Pi 3's entire budget). This file surveys real alternatives against the same bar, framed by Joakim's actual hardware vision: modular, easy-upgrade consumer hardware (buy a bigger SSD, add a module, no forced platform migration) and his "torrent-solution where even private files could be split up on different machines and only I know how to assemble them" framing.

## Verdict

**Garage and Tahoe-LAFS are both real, currently-viable candidates — Garage is the closer match to this project's actual deployment shape (home routers over the internet); Tahoe-LAFS is the closer match to the "split up, only I can reassemble" framing specifically.** Neither has been tested against this project's exact workload; both need real hands-on evaluation before either gets adopted, not just this literature check.

## Tahoe-LAFS — closest match to "split up private files, only I can reassemble"

An existing, open-source, actively-maintained ("Least-Authority File Store") distributed storage system built exactly around Joakim's framing:

- **How it works**: a file is encrypted first (AES-CTR), then the *ciphertext* is split via erasure coding into shares spread across multiple storage servers — by default, 10 shares across at least 7 distinct servers, and any 3 of those 10 are enough to reconstruct the file. Losing up to 7 of the 10 storage servers still doesn't lose the file.
- **Who can read it**: only whoever holds the decryption key — a storage server holds meaningless encrypted shares and can't read the data itself, matching this project's "leased"-tier design (encrypted, key stays with the owner) almost exactly.
- **Resource footprint**: genuinely lightweight in the *storage server* role specifically — Tahoe-LAFS's own FAQ states the storage server "runs okay" on a device with 64 MB of RAM (a NAS box far weaker than a Pi 3), because it never does encryption/decryption/erasure-coding itself — it just stores opaque encrypted blocks. The heavier role (the "gateway," which does the encryption/erasure-coding/key-handling) needs more, but real deployment reports confirm it running on a Raspberry Pi (Raspbian) in both client and storage-node roles.
- **Maintenance status**: actively maintained — version 1.20.0 released December 2024, a Python 3.13 compatibility fix in September 2025, and Open Collective funding activity through mid-2026. Not an abandoned project.
- **What's unverified**: no source found benchmarks the *gateway* role specifically on Pi-3-class hardware (1 GB RAM) under this project's realistic workload (family photo library scale) — the 64 MB figure is for the lighter storage-server role only.

## Garage — closest match to this project's actual deployment shape

A newer (in production since 2020, actively maintained, v2.3.0), single-binary Rust project built by the Deuxfleurs collective, S3-compatible (speaks the same API as Amazon S3/MinIO):

- **Explicitly designed for this project's exact scenario**: geo-distributed nodes on modest hardware, built to tolerate real home-internet conditions — its own documentation states it's designed to run on Raspberry Pis and tolerate ~200ms latency between nodes, i.e., separate homes' routers talking to each other over ordinary internet, not a datacenter LAN.
- **How redundancy works**: full replication (typically 3 copies), not erasure coding — simpler than Tahoe-LAFS's scheme, at the cost of more raw storage overhead per byte (roughly 3x, in the same ballpark as Tahoe-LAFS's default 10-shares-need-3 ratio, just via copies instead of coded shares).
- **Why it's on this list now and wasn't before**: MinIO — the previous default "self-hosted S3" choice — **ceased development and archived its community edition in April 2026**, with multiple security bugs and explicit recommendations against continued use. Garage has become the most-recommended replacement specifically because of this.
- **What's unverified**: no source found gives an exact RAM figure for Garage on a Pi 3 specifically (general claims say "light enough," not a measured number) — needs a real test, not just documentation claims.

## Others checked

- **SeaweedFS**: lighter-weight design than MinIO, its master process reportedly runs under 30 MB, and it supports erasure coding without MinIO's rigid symmetric-disk-layout requirement — a real second-tier candidate, though volume servers reportedly want 2-4 GB RAM, more than a Pi 3 has.
- **MinIO**: **ruled out regardless of resource footprint** — ceased development, community edition archived April 2026, multiple known security bugs, explicitly discouraged by current sources.
- **Syncthing** (already named as prior art in this file's README): confirmed lightweight in typical use (can stay under 30 MB RAM) but is continuous block-level *sync* between devices, not a redundancy/erasure-coding system — it doesn't solve "my files survive my own hardware dying," only "my files stay copied to wherever I've told it to sync," which is a different problem than this file's DFS question.
- **Bare/standalone Kademlia DHT libraries** (e.g. Rust crates like `rust-kad`, `kademlia-dht`): several exist, but none found are positioned or proven for production embedded/low-memory use — mostly small or educational implementations. Not a ready-made foundation the way Tahoe-LAFS or Garage already are.
- **Perkeep** (formerly Camlistore): no resource-requirement or Raspberry Pi data found in this research pass — flagged as a gap, not evaluated.

## What's still open

Neither Tahoe-LAFS nor Garage has been tested against this project's actual workload (real family-photo-library sizes, real home-router network conditions, alongside this project's own app running on the same constrained device) — this research answers "is it plausible," not "is it proven for us." A real hands-on trial on actual Pi-class hardware is the next step, not a foregone adoption decision — see [TODO.md](TODO.md)'s RPi3 stress-test item (also raised 2026-07-29, in [../photo-server/TODO.md](../photo-server/TODO.md)) for the broader push to test on real hardware before committing further design to any of this.

## Status

Researched 2026-07-29, all lookups logged per this project's research-log convention. Paper research only — no adoption decision made, Pillar 1 per [../VISION.md](../VISION.md)'s reaffirmed scope.
