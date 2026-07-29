# Glossary

Plain-language definitions of every technical/business term this project's design docs use, written for a non-specialist reader. See [CLAUDE.md](../CLAUDE.md)'s non-negotiable rule: every term explained in conversation gets added here, same turn, no exceptions. Design docs keep the full technical detail in their own home file; this file is the quick, jargon-free reference — link here instead of re-explaining a term inline.

## Ownership and sharing

- **Strict tier**: a photo stays visible only to its owner; a revocable viewing grant can be given to someone else, but she never gets an independent, durable copy — the owner can cut off access at any time. See [distributed-sync/OWNERSHIP.md](distributed-sync/OWNERSHIP.md).
- **Leased tier**: a photo can be durably copied onto other people's storage for redundancy, but stays locked (encrypted) with a key only the owner controls — revocable by the owner withholding/rotating that key, even though the locked bytes may still physically exist elsewhere. See [distributed-sync/OWNERSHIP.md](distributed-sync/OWNERSHIP.md).
- **Free tier**: a full, permanent, irrevocable transfer — the recipient becomes a genuine independent owner and can do anything with her own copy, including reshare it further. See [upload-and-share/OWNERSHIP.md](upload-and-share/OWNERSHIP.md).
- **`photo_owners` row**: the database record that says "this specific user owns/can access this specific photo" — sharing adds a new row pointing at the same underlying bytes, it never duplicates them.
- **Tag visibility vs. ownership tier — two separate axes**: a photo's strict/leased/free tier controls who can see the *photo*; a tag's own private/shareable setting controls who can see *that tag* (a name, a label) — independently. A free (fully shareable) photo can still carry a private tag nobody else ever sees.
- **Mutual-acceptance sharing / `open` mode**: the default rule that nobody can share something with you unless you accept it first; a per-user opt-out (`open` mode) lets someone skip that step, currently gated behind an unbuilt safety feature (see "nudity/NCII classifier" below).
- **Blocking**: a user-to-user block that always overrides any other setting — a blocked person can never share with you again, no exceptions.

## Distributed storage and networking (the future "Pillar 1" vision)

- **DFS (distributed file system)**: instead of all photos living on one server, they're spread redundantly across several independent computers (e.g. your own future home NAS plus relatives' own devices), so losing any single one doesn't lose the photos.
- **Node**: one participating computer in the DFS (e.g. one person's home NAS box).
- **DHT (distributed hash table)**: a shared "address book" with no single owner — every participating node holds a small slice of "who's storing what," and a lookup question gets passed node-to-node until it's answered. This is how BitTorrent already finds who's sharing a file; no payment or competition involved, just cooperative bookkeeping. **Kademlia** is the specific DHT algorithm this project's research keeps running into — the one both IPFS and BitTorrent's trackerless mode use.
- **IPFS / Kubo**: a specific, ready-made open-source implementation of a DHT plus content-addressing. **Ruled out for this project's target hardware, 2026-07-29** — Kubo (its reference implementation, renamed from `go-ipfs`) recommends 6 GB RAM, about 6x a Raspberry Pi 3's entire budget. See [distributed-sync/TODO.md](distributed-sync/TODO.md).
- **Content-addressed storage**: a file's "address" is derived from its own contents (a fingerprint/hash of the bytes), so identical files always get the same address and storage is automatically deduplicated. This project's storage already works this way.
- **Erasure coding / secret sharing**: splitting a file into several pieces such that only *some* of them (not all) are needed to reconstruct it — gives redundancy (losing a few pieces is fine) without needing a full copy on every node.
- **Shard**: one piece of a file after erasure coding/secret-sharing has split it up.
- **Replication (storage redundancy)**: the simpler alternative to erasure coding — instead of splitting a file into shards, just keep several full copies (e.g. Garage's default of 3) on different nodes. Costs more raw storage per byte than erasure coding but is simpler to reason about.
- **Proof of Work (PoW)**: the mechanism behind Bitcoin-style mining — everyone competes at a deliberately pointless, hard computational puzzle; winning it first lets you record the next entry in a shared ledger and earns a reward. Secure because cheating is expensive, but that expense is real electricity/hardware cost, which is exactly why it doesn't fit small/constrained hardware.
- **Proof of Stake (PoS)**: an alternative to PoW — instead of a computing race, participants lock up real money/tokens as collateral; cheating loses you the deposit. Far less energy use, but needs a valuable token to stake in the first place.
- **Proof of Useful Work (PoUW)**: the idea of replacing PoW's pointless puzzle with something actually useful (e.g. AI inference). A real research area (back to Primecoin, 2013) but **immature** — research found in 2026 that a real deployed AI-flavored version had zero actual inference happening; nobody's solved cheaply proving the claimed useful work was real. See [distributed-sync/TODO.md](distributed-sync/TODO.md).
- **Blockchain**: a shared, tamper-evident ledger multiple parties agree on without a central authority — solves "who agrees on what's true," a different problem from a DHT's "who has this file."
- **Marketplace** (as used in this project's docs): any system where money changes hands for content or storage — e.g. Adobe Stock selling photographers' work, or Filecoin/Storj renting out spare disk space for payment. Not a reference to Facebook's product of the same name.
- **Tahoe-LAFS**: an existing open-source "Least-Authority File Store" using erasure coding + encryption specifically so no single storage node can read your data and only a threshold of shards is needed to reconstruct it — see [distributed-sync/NETWORK_MECHANISM.md](distributed-sync/NETWORK_MECHANISM.md) for the full research on whether it fits this project.

## Security and privacy

- **Encryption-at-rest**: data is stored scrambled (encrypted) and only readable by whoever holds the right key — protects the data while it's sitting on a disk, but says nothing about what happens once someone legitimately unlocks it.
- **Decryption key / key-gating**: the "password" that unlocks encrypted data; controlling who holds a valid key is how this project controls who can actually access something, independent of who physically stores the encrypted bytes.
- **JWT (JSON Web Token)**: a compact, signed token format used to prove who's logged in without the server needing a database lookup on every request. This project issues a short-lived JWT (5 min) plus a longer-lived refresh token, both Redis-backed so either can be revoked early — see [policies/AUTHENTICATION.md](policies/AUTHENTICATION.md).
- **Passkeys / WebAuthn**: a W3C standard letting a user log in with a device-held key pair (fingerprint, face unlock, or a hardware key) instead of typing a password — verified locally against public keys the app itself stores. No third-party **relying party** (an external identity-verification service) is involved, unlike OAuth, so this stays inside the closed-by-default posture — see [policies/AUTHENTICATION.md](policies/AUTHENTICATION.md).
- **k-anonymity**: a way to query a database without revealing exactly what you're asking about — the client sends only a short prefix of a value's hash, and the server returns every match for that prefix, so it never learns which specific value (e.g. password) was checked. This is how Have I Been Pwned's public breached-password API works.
- **Homomorphic encryption (HE) / secure multiparty computation (MPC)**: cryptographic techniques that let two parties compare or compute on encrypted data *without ever decrypting it*. Real, active research with genuine speed on server-class hardware, but not proven to run on small/constrained devices yet.
- **Biometric data / "special category" data**: under GDPR, data specifically processed to uniquely identify a person (a face embedding used for matching) gets extra-strict legal protection — a plain photo alone does not automatically count.
- **Face embedding**: a numeric fingerprint a face-detection model computes from a face — not a photo, but real peer-reviewed research shows it can often be turned back into a recognizable face image, so it isn't automatically "safe" just because it isn't a picture.
- **ISO/IEC 24745**: the real international standard for protecting biometric data at rest — requires that any stored biometric reference be irreversible (can't be turned back into the original), unlinkable (can't be cross-matched across databases), and renewable/revocable. Caveat from the research: published schemes that *claim* irreversibility have been found reversible in practice — don't trust a scheme's own claim without independent adversarial testing.
- **EDPB (European Data Protection Board)**: the EU's top coordinating body for privacy law — every EU country's own privacy watchdog (Sweden's is IMY) meets here to issue official, EU-wide rulings. About as authoritative as EU privacy guidance gets.
- **CJEU (Court of Justice of the European Union)**: the EU's highest court — its rulings are binding across every member state, including Sweden. Relevant here for *Lindqvist* and *Rynes*, the two cases underpinning GDPR's household exemption below.
- **GDPR**: the EU's general data protection law — applies to this project directly, since it's Sweden-based (an EU member state), not just as a hypothetical concern about other people's users.
- **Household / personal-activity exemption**: GDPR's carve-out for purely private/family use (Article 2(2)(c); e.g. keeping your own family's photos on your own laptop) — stops applying the moment an activity reaches out to an "indefinite number of people" outside that private circle, per CJEU case law (*Lindqvist*, *Rynes*).
- **NCMEC**: the US National Center for Missing & Exploited Children, the US body that receives mandatory reports of child sexual abuse material — this project's actual applicable reporting regime is Swedish/EU, not researched yet (see [policies/POLICY.md](policies/POLICY.md)).
- **CSAM (Child Sexual Abuse Material)**: the standard term for illegal content depicting child sexual abuse — moderation (the perceptual-hash blocklist) overrides ownership/sharing terms unconditionally for this category, see [policies/POLICY.md](policies/POLICY.md).
- **NCII (non-consensual intimate imagery)**: explicit images shared or distributed without the depicted person's consent — the category an on-device nudity/NCII classifier is meant to catch before display, see [upload-and-share/ABUSE_MITIGATION.md](upload-and-share/ABUSE_MITIGATION.md).
- **PDQ hash / perceptual hash**: a fingerprint of an image's visual content (not its exact bytes) used to detect known illegal/flagged content even if it's been resized or slightly altered — this project's planned moderation mechanism.

## Tags and entities

- **Entity**: one reusable record for a recurring person/object/animal/place (e.g. "Dad," "my dog Bella") that many individual photo tags can point to, so searching "every photo of my dog" is one search instead of many separately-worded tags.
- **Bounding box**: the pixel-coordinate rectangle marking where a detected person/object sits within a photo.
- **Relationship tag**: a tag that links two other tags together (e.g. "my father," pointing at his own person-entity) rather than describing the photo directly.

## Legal / business

- **Skatteverket**: Sweden's tax agency — the actual applicable authority for any future marketplace/income feature, not the US IRS citations an earlier research pass mistakenly used.
- **Moms**: Swedish for VAT (value-added tax) — relevant if a future marketplace feature ever sells digital goods/services.
- **ROI** (as used in this project's storage-incentive brainstorm): "return on investment" — here, whether the durability benefit of contributing spare storage to the network outweighs the simpler cost of just keeping photos on your own phone/NAS.
- **Payment facilitation**: the legal/regulatory burden of handling money transfers between two other parties (e.g. a marketplace paying sellers out) — normally requires a money-transmission license. **Stripe Connect** is the standard industry pattern for outsourcing this, because it absorbs that licensing burden rather than a project having to become a licensed money transmitter itself.

## Status

Created 2026-07-29. Living document — append new terms here as they come up in conversation, per `CLAUDE.md`'s non-negotiable rule, rather than letting an explanation exist only in chat.
