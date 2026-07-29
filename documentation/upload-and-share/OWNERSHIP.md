# Ownership model

Every user who uploads a photo owns her own copy (`photo_owners` row in [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)), regardless of who else can also see it. Sharing never duplicates the underlying bytes (see [UPLOAD.md](UPLOAD.md)'s Storage layout) — it adds another `photo_owners` row pointing at the same `photos` row, so "her own copy" is a real ownership record, not a metaphor.

## Strict vs. free

Set per photo, with a per-album/tag **default** a host/owner can set once and override per photo (e.g. "this whole wedding album is free" with one photo flipped back to strict).

| | **Strict** | **Free** |
|---|---|---|
| Resharing onward | Blocked — sharee can't expose it to a new person without asking the original owner | Allowed, including by anyone further down the chain |
| Download/export of the original file | Blocked | Allowed |
| Revocable by the owner | Yes, at any time | **No — irrevocable once shared.** "If once shared as free, you cannot take it back" |
| Access mechanism, this stage (one server) | A live permission check against `photo_owners.sharing_terms` on every view — no separate file, no local cache; revoking the row (or flipping it off) ends access on the next request | A genuine, independent `photo_owners` row — hers to view, download, or reshare like anything else she owns |
| Tagging/annotating the sharee's own copy | **Always allowed, both tiers** — see below | Always allowed |

**Tagging is never gated by strict/free — and this is a separate axis from tag
visibility, not the same mechanism.** `tags` is already keyed
`unique(photo_id, user_id, tag)` — every user's tags on a photo are her own rows,
not attached to the photo globally. So a sharee can always add her own tags to a
photo she can see, regardless of the owner's strict/free setting. What actually
governs whether *that tag* is ever seen by anyone else is a second, narrower axis —
each tag's own `private`/`shareable` visibility, independent of the photo's
ownership terms — see [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s Privacy section
for the full model. Maximizing tagging volume is the whole point of this system
(training data for the prediction model, see [../VISION.md](../VISION.md) Pillar 2)
— ownership terms exist to control *photo* exposure/redistribution; tag visibility
controls *tag* exposure; neither one gates *annotation* itself.

**Reshare chain, resolved:** a **free** share is a full, irrevocable transfer of co-ownership — the new sharee is a real independent owner from that point on, sets her own terms for her own further shares, and the original owner has no further say or visibility into what happens downstream. A **strict** share is never ownership at all — it's a revocable viewing grant, enforced the same way every other authorization check in this app already works (session + a scoping join, see [../photo-server/TODO.md](../photo-server/TODO.md)'s cross-cutting security checklist) — no new protocol needed at this stage.

## Relationship to the future DFS pillar (not designed here)

Raised during this design conversation: a strict share's revocability is in tension with the DFS vision's goal of sharees' hardware contributing real storage/redundancy ([../VISION.md](../VISION.md) Pillar 1) — durable bytes on someone else's node are hard to reconcile with "revoke instantly, no trace left behind." **This stage is explicitly one server only, not a network of user NAS/routers** — that tension is real but belongs to [distributed-sync/](../distributed-sync/README.md)'s future design once a second real node exists, not to this doc. Nothing here should be read as designing that network layer now; `photo_owners.sharing_terms` and `shared_from_owner_id` are the only additions this stage actually needs, and they work the same whether or not a second node ever appears — see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md). Paper-stage resolution (a third, key-gated "leased" tier, plus access/storage-contribution as orthogonal axes): [../distributed-sync/OWNERSHIP.md](../distributed-sync/OWNERSHIP.md) — still doesn't change this stage's strict/free pair.

Storj/Filecoin (erasure coding vs. replication) and SyncThing (rejected as a base to build ownership on, no such concept exists in it) were checked as prior art for *that future* problem, not this stage's — see [distributed-sync/README.md](../distributed-sync/README.md)'s tool table for where that inventory actually lives.

## Moderation — supersedes ownership entirely, not a sharing-permission question

See [../policies/POLICY.md](../policies/POLICY.md)'s "Moderation supersedes ownership" rule — a hard, project-wide constraint, not just a design note here.

Proposed mechanism: every ingested/uploaded photo gets a perceptual hash via **[PDQ](https://github.com/jankais3r/jPhotoDNA)** (Facebook's open-source, BSD-licensed algorithm — not the proprietary, licensing-encumbered PhotoDNA). A reserved `blocklist_hashes` table (admin-only writes, see [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)) holds flagged hashes; any match — at ingest or retroactively — quarantines the photo network-wide, full stop. Later, once real multiple nodes exist, hash-blocklist propagation across nodes is exactly how NCMEC/IWF's real-world inter-platform hash-sharing already works — same pattern, smaller scale.

**Not resolved here, flagged plainly:** once the event/party feature ([EVENTS.md](EVENTS.md)) lets people upload without an account, this project likely takes on real legal reporting obligations for illegal content (e.g. NCMEC CyberTipline duties under US law). That is a lawyer question, not an engineering one — don't treat anything above as legal clearance; get real legal advice before "anyone can upload, no account" ships for real.

## Status

Designed 2026-07-26 (branch `upload-and-share`). No schema migration, no endpoints. See [../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md) for the resulting reserved-table additions and [TODO.md](TODO.md) for what's still open before build steps get written.
