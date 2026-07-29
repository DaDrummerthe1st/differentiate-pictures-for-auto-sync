# Metadata privacy under the DFS — paper design, not built

Scope: Pillar 1/2 per [../VISION.md](../VISION.md)'s reaffirmed scope, paper only. Extends [OWNERSHIP.md](OWNERSHIP.md)'s strict/leased/free tiers to the *metadata* (tags/entities) describing a photo, not just the photo's bytes — partially answering [TODO.md](TODO.md)'s open "where does metadata live" question. Which network mechanism actually carries this metadata (DHT vs. blockchain, and the "sell photos through the network" marketplace idea's implications) is still under active research — see [TODO.md](TODO.md); the exposure-boundary theory below doesn't depend on which mechanism wins that question.

## Raw tag data vs. aggregate/derived signal — two different exposure classes

[../tags/TAXONOMY.md](../tags/TAXONOMY.md) already separates tag *visibility* (private/shareable) from photo *ownership* terms — a free photo can still carry a private tag. This extends that same separation to the network layer: a photo's strict/leased/free tier governs whether its **bytes** replicate; it should never, by itself, decide whether the **names of people in it** become network-visible. Conflating the two — "this photo is free, therefore its tags are public" — would leak person-identifying data ([../security/THREATS.md](../security/THREATS.md) #1, #4) as a side effect of a redistribution decision, not a privacy one.

- **Raw tag/entity content** (a person's name, "Dad", a relationship link) stays owner-controlled regardless of the photo's own tier.
- **Aggregate/derived signal** — embeddings, usage counts (`downloaded_at`/`download_count`, [../tags/SCHEMA.md](../tags/SCHEMA.md)) — is the layer [../VISION.md](../VISION.md) Pillar 2 already wants shared network-wide ("learned globally across the network"). This is the real candidate for open publication: an anonymous index of embeddings and engagement counts, never attached to whose face/name they represent.

## Bounding boxes are the only thing a shared photo ever exposes

A shared/free-tier photo carries at most a generic bounding box ("a human is here") — never a name or entity link, which stays in the tagging user's own private index, never attached to the box for anyone else. Later, a bounding box could carry crowd-sourced, non-identity aggregate impressions ("65% of viewers guess: man, late 70s") — a social-consensus statistic, not an identity claim, and never traceable to a specific person. This is the resolved design, confirmed 2026-07-29: no other user ever learns who *you* call "Dad," and no server-side "who is this" answer ever exists to leak.

## Private, per-user face matching — resolved 2026-07-29

Every user holds her own private face index (reference embeddings for people she's tagged), never shared with or visible to anyone else, ever. To find more photos of someone she already knows, she searches only among photos she **already has legitimate access to** (owned, or shared/leased/free to her) — her own device runs her own model against those already-accessible photos' bounding boxes, entirely locally.

This needs no published index, no shared embeddings, and no server-side matching, **at any scale** — not just at today's household size. It works the same way whether she has 50 accessible photos or 50,000, because the mechanism only ever touches photos she can already open; there is no scenario in this design where she searches photos she has no access to. The earlier framing of this as a scale problem (small household vs. a 65,000-person venue) was a mistake — access, not scale, is what bounds the search, and access is already fully governed by [OWNERSHIP.md](OWNERSHIP.md)'s tiers.

The EDPB/reconstruction-attack research (Mai et al., IEEE TPAMI 2018; EDPB Opinion 11/2024 — see [../security/TODO.md](../security/TODO.md) item 6) still matters here for one reason: it's why no version of this should ever publish raw embeddings anywhere, which this design already doesn't do.

## Status

Paper design, 2026-07-28/29, security-researched and scope-corrected 2026-07-29. Not built, not scheduled — Pillar 1/2 per [../VISION.md](../VISION.md)'s reaffirmed scope. The network/consensus mechanism (DHT/IPFS — see [TODO.md](TODO.md), IPFS itself ruled out for Pi-class hardware 2026-07-29) and the marketplace idea remain open threads; face-matching privacy is fully resolved, not an open question.
