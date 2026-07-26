# Ownership model

Every user who uploads a photo owns her own copy (`photo_owners` row in [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)), regardless of who else can also see it. Sharing never duplicates the underlying bytes (see [UPLOAD.md](UPLOAD.md)'s Storage layout) — it adds another `photo_owners` row pointing at the same `photos` row, so "her own copy" is a real ownership record, not a metaphor.

## Strict vs. free

Set per photo, with a per-album/tag **default** a host/owner can set once and override per photo (e.g. "this whole wedding album is free" with one photo flipped back to strict).

| | **Strict** | **Free** |
|---|---|---|
| Resharing onward | Blocked — sharee can't expose it to a new person without asking the original owner | Allowed, including by anyone further down the chain |
| Download/export of the original file | Blocked | Allowed |
| Revocable by the owner | Yes, at any time | **No — irrevocable once shared.** "If once shared as free, you cannot take it back" |
| What the sharee's node stores | Encrypted pieces only (see below) — never enough to reconstruct or view without a live, owner-issued key | A durable, independently viewable copy — real co-ownership |
| Viewing when the owner is offline | **No** — strict access is a live, streamed, key-gated view. No owner online, no view, even from the sharee's own device, even against her own previously-cached pieces | Yes — it's fully hers |
| Tagging/annotating the sharee's own copy | **Always allowed, both tiers** — see below | Always allowed |

**Tagging is never gated by strict/free.** `tags` is already keyed `unique(photo_id, user_id, tag)` — every user's tags on a photo are her own private rows, not attached to the photo globally. So a sharee can always add her own location/person/quality/comment tags to a photo she can see, regardless of the owner's strict/free setting, and the owner's *other* private tags on that same photo (e.g. an embarrassing in-joke) never travel to the sharee in the first place — she was never sharing that tag, only the photo (and, if she chose to share the containing tag/album itself, that album's name). Maximizing tagging volume is the whole point of this system (training data for the prediction model, see [../VISION.md](../VISION.md) Pillar 2) — ownership terms exist to control *exposure/redistribution*, never to gate *annotation*.

**Reshare chain, resolved:** a **free** share is a full, irrevocable transfer of co-ownership — the new sharee is a real independent owner from that point on, sets her own terms for her own further shares, and the original owner has no further say or visibility into what happens downstream. A **strict** share is never ownership at all — it's a revocable, streamed viewing grant; nothing the sharee's node holds is independently useful without the owner.

## Torrent-style piece distribution (foundation only, not built this iteration)

For a **strict** share to actually contribute to the DFS vision's storage-offloading goal ([../VISION.md](../VISION.md) Pillar 1) without breaking revocability, the sharee's node should be able to hold real bytes — just not *usable* bytes without the owner's cooperation:

- The owner's node always retains her own full, authoritative copy. Distributing pieces to sharees is additional redundancy, never a replacement for the owner's own retention — this is what stops "none of the sharees are available" from ever locking the owner out of her own picture.
- A sharee's node can durably store an **encrypted piece** of a strict-shared photo (real bytes, contributing to redundancy and — later — a storage-credit ledger), but viewing requires the owner's node to issue a short-lived decrypt/reconstruction key per session. No owner online → no new key → no view, even from the sharee's own already-cached ciphertext. This is what makes "streaming, not persistent" true for the *sharee's access*, while still true that her hardware is durably holding bytes that matter to the *owner's* redundancy.
- A **free** share needs none of this machinery — the sharee gets the genuine file (or enough pieces to always reconstruct it herself), because that's what "free" means.

Today, with one server, this whole mechanism is moot (the one node holds everything anyway) — it's written down now so `photo_owners` and a future reserved storage-credit ledger don't need reshaping when a second real node exists.

**Studied for the redundancy/credit design, not adopted**: Storj (erasure coding, no replication) and Filecoin (replication plus on-chain proof) show the two main strategies for this trade-off; a blockchain/token layer is out of scope for a private household project, but the storage-proof pattern is the relevant part. [distributed-sync/README.md](../distributed-sync/README.md)'s SyncThing/rclone table stays the transport-layer inventory — this piece-distribution idea is a layer above raw sync, not a replacement for it. **SyncThing itself was evaluated and rejected as a base to build the ownership layer on**: P2P, TLS end-to-end, no central server, but requires both peers online simultaneously (no store-and-forward) and has no concept of per-user ownership terms, an invite/share-token system, moderation, or a credit ledger — none of this project's actual product exists in it to reuse. It stays a candidate purely for raw device-to-device *transport* once a second real node exists; writing the ownership/metadata layer from scratch isn't reinventing a wheel that already exists elsewhere.

## Moderation — supersedes ownership entirely, not a sharing-permission question

Ownership terms (strict/free) govern who may see or redistribute *legitimate* content. They have **no bearing whatsoever** on illegal or abusive content (CSAM, non-consensual imagery, harassment) — that's a categorically different axis, an admin-level override that removes content unconditionally, regardless of any owner's or sharee's claimed rights. See [../policies/POLICY.md](../policies/POLICY.md)'s "Moderation supersedes ownership" rule — this is a hard, project-wide constraint, not just a design note here.

Proposed mechanism: every ingested/uploaded photo gets a perceptual hash via **[PDQ](https://github.com/jankais3r/jPhotoDNA)** (Facebook's open-source, BSD-licensed algorithm — not the proprietary, licensing-encumbered PhotoDNA). A reserved `blocklist_hashes` table (admin-only writes, see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)) holds flagged hashes; any match — at ingest or retroactively — quarantines the photo network-wide, full stop. Later, once real multiple nodes exist, hash-blocklist propagation across nodes is exactly how NCMEC/IWF's real-world inter-platform hash-sharing already works — same pattern, smaller scale.

**Not resolved here, flagged plainly:** once the event/party feature ([EVENTS.md](EVENTS.md)) lets people upload without an account, this project likely takes on real legal reporting obligations for illegal content (e.g. NCMEC CyberTipline duties under US law). That is a lawyer question, not an engineering one — don't treat anything above as legal clearance; get real legal advice before "anyone can upload, no account" ships for real.

## Status

Designed 2026-07-26 (branch `upload-and-share`). No schema migration, no endpoints. See [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md) for the resulting reserved-table additions and [TODO.md](TODO.md) for what's still open before build steps get written.
