# Ownership under the DFS — paper design, not built

Scope note per [../VISION.md](../VISION.md)'s reaffirmed 2026-07-27 line: Pillar 1 territory, paper only. Nothing here changes [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)'s one-server strict/free model, which stays exactly as designed and unaffected by this file. This is the resolution to the tension that doc's "Relationship to the future DFS pillar" section named but explicitly declined to design, and to [TODO.md](TODO.md)'s matching open question — worked through now, on paper, so it exists once a second real node does.

## Three tiers, once a second node exists

Extends the one-server strict/free pair into three, because "revocable" and "sharee's hardware contributes durable, creditable storage" can't both be true of the same mechanism once bytes actually leave the owner's node:

- **Strict** — tightened for the DFS case: content under strict terms is **never replicated onto any node but the owner's own**. No redundancy benefit, full privacy — access ends the moment the owner's own node does, and that's the accepted price. Ownership authority stays absolute: only the owner ever has access, DFS or not.
- **Leased** (new) — durable and replicated as encrypted shards across other nodes (real redundancy/storage credit, same as free), but decryption is gated by a key the owner holds. Revocation = the owner withholds or rotates that key for a given sharee; the shards can stay physically present on other nodes and become permanently unreadable to whoever was revoked. Named "leased" rather than "shared" specifically to avoid colliding with "sharing" as this project's general term for the whole mechanism (`SHARING.md`, "share this photo/album") — every sentence describing this tier would otherwise say "shared" twice with different meanings. The actual key-rotation/encryption scheme is not designed here — it needs the same authoritative-sources-only research bar as [../security/TODO.md](../security/TODO.md)'s item 6 (facial-recognition data under a distributed store is the same underlying "encrypted at rest, keyed so only the right party can decrypt" problem), not a guessed crypto design.
- **Free** — unchanged from `upload-and-share/OWNERSHIP.md`: irrevocable, full co-ownership transfer, the sharee's copy is a genuinely independent one from that point on, torrent-style.

Owner authority is final once she sets **free** — permanently, no later recipient can re-tighten it. **Strict** and **leased** both stay under her control indefinitely (immediate cutoff for strict, key-revocation for leased); **free** is the one tier that's a real, final transfer of that authority.

## Two orthogonal axes: access tier vs. storage contribution

The storage-space scenario below only resolves cleanly once these are treated as separate mechanisms:

- **Access tier** (strict/leased/free) — who can *decrypt and view* the content, and who controls that.
- **Storage contribution** — which node's spare capacity happens to host a given encrypted shard, for DFS redundancy/credit purposes (Storj/Filecoin-style: a storage node hosts anonymous ciphertext shards for network credit; it doesn't need to know or care what it's storing).

For **leased** and **free** content, these two axes are decoupled — a node can go on hosting a shard of something regardless of whether the person who runs that node still has (or ever had) decrypt access to it. For **strict** content, they're coupled by definition: no replication happens at all, so there's no separate storage-contribution question to ask.

## Worked example: the storage-space scenario

User1 shares an album, **leased** tier, with User2, User3, and User4.

- **User2 and User3 accept.** Each gets a key/token from User1 and can decrypt and view the album. Their nodes may also end up hosting encrypted shards of it (theirs or others' redundancy pieces) as part of the DFS's normal shard-placement — an entirely separate fact from their having accepted the share.
- **User4 never accepts.** No key is ever issued to her, no shard placement is ever made relative to her acceptance, nothing exists to revoke. Clean — this case needs no special handling under the model above.
- **User3 later "deletes" the album** — removes it from her own library/view, i.e. she no longer wants decrypt access or a local reference to it. This does not, by itself, mean her node stops hosting whatever encrypted shard(s) it was already contributing to the redundancy pool for that content: shard hosting is a storage-contribution fact, not an access-tier fact, and under erasure coding a single shard is meaningless without the others anyway. She keeps silently serving those pieces.
- **User3 later wants the space back.** Only *now* does the storage-contribution question actually get resolved: the DFS has to place that shard on another node first (standard redundancy-factor rebalancing) before her space is actually freed — same mechanical problem any Storj/Filecoin-style network already solves, not something specific to ownership tiers.

## Status

Paper design, 2026-07-28. Not built, not scheduled — Pillar 1 per [../VISION.md](../VISION.md)'s reaffirmed scope; nothing here should influence any current-phase schema/UX decision. Revisit alongside [TODO.md](TODO.md)'s other open questions once a second real node exists.
