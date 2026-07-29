# Metadata privacy under the DFS — paper design, not built

Scope: Pillar 1/2 per [../VISION.md](../VISION.md)'s reaffirmed scope, paper only. Extends [OWNERSHIP.md](OWNERSHIP.md)'s strict/leased/free tiers to the *metadata* (tags/entities) describing a photo, not just the photo's bytes — partially answering [TODO.md](TODO.md)'s open "where does metadata live" question. Which network mechanism actually carries this metadata (DHT vs. blockchain, and the "sell photos through the network" marketplace idea's implications) is still under active research — see [TODO.md](TODO.md); the exposure-boundary theory below doesn't depend on which mechanism wins that question.

## Raw tag data vs. aggregate/derived signal — two different exposure classes

[../tags/TAXONOMY.md](../tags/TAXONOMY.md) already separates tag *visibility* (private/shareable) from photo *ownership* terms — a free photo can still carry a private tag. This extends that same separation to the network layer: a photo's strict/leased/free tier governs whether its **bytes** replicate; it should never, by itself, decide whether the **names of people in it** become network-visible. Conflating the two — "this photo is free, therefore its tags are public" — would leak person-identifying data ([../security/THREATS.md](../security/THREATS.md) #1, #4) as a side effect of a redistribution decision, not a privacy one.

- **Raw tag/entity content** (a person's name, "Dad", a relationship link) stays owner-controlled regardless of the photo's own tier.
- **Aggregate/derived signal** — embeddings, usage counts (`downloaded_at`/`download_count`, [../tags/SCHEMA.md](../tags/SCHEMA.md)) — is the layer [../VISION.md](../VISION.md) Pillar 2 already wants shared network-wide ("learned globally across the network"). This is the real candidate for open publication: an anonymous index of embeddings and engagement counts, never attached to whose face/name they represent.

## Bounding boxes public, names private — feasible, with one caveat

`tag_references.bounding_box` ([../tags/SCHEMA.md](../tags/SCHEMA.md)) is pixel geometry, stored independently of `reference_value` (the entity it names). Publishing box geometry without the entity link is straightforward — it says "a detectable region existed here," not whose. This genuinely stops *automated* cross-photo linking: an algorithm can't assemble "every photo of Dad" from public data if the entity id never leaves the owner's own node.

**What it doesn't stop**: a human looking at an already-public (free-tier) photo can still visually recognize a face, box or no box, name or no name. The privacy win here is "stops automated re-identification at scale," not "stops a viewer who already recognizes the person."

## Private, per-user cross-network face matching — researched 2026-07-29, sketch revised

Raised 2026-07-28: a user wants to find more photos of someone she already has a private reference for (e.g. "Dad") — searching not just her own tagged photos but the wider network's free/leased-tier photos too, via her own on-device face-embedding model, without that search or its results ever becoming visible to anyone else.

**Scope clarification, 2026-07-29 — this is two different problems, not one**, and conflating them is what made the original sketch look harder than it needs to be at the scale this project actually operates at today:

- **Searching photos already shared with you** (the entire realistic case at V1/V2 scale — one household plus invited relatives): if a photo is already accessible to a user (she has a `photo_owners` row or a leased-tier key for it), her own device can simply run her own face-detection model directly against those already-decrypted photos she's already allowed to see. This needs **no new mechanism at all** — no public index, no embedding-sharing, nothing beyond "run local search over my own accessible library." This covers what Joakim described: her own model computes a reference vector for "dad" and checks it against photos she can already open.
- **Searching photos you have no relationship to at all** (only becomes a real scenario at V3's "everyone, 65,000-person-venue" scale, per Joakim's 2026-07-29 vision-timeline note, [TODO.md](TODO.md)): this is the actual hard case the EDPB/reconstruction-attack research above addresses — searching a public commons of strangers' photos needs some shared index or matching mechanism, which is exactly where the "don't publish raw embeddings" finding applies. **Not needed for V1 or V2.**

**Original sketch (superseded)**: a public, anonymous index of face-embedding vectors (photo/region pointer + embedding, no name/entity attached), with each user's client matching her own private reference against it locally. Research against authoritative sources (EDPB, NIST, peer-reviewed reconstruction-attack literature — see [../security/TODO.md](../security/TODO.md) item 6 for full findings) found this doesn't hold up:

- **A face embedding is not safe to publish just because it isn't a photo.** Peer-reviewed work (Mai et al., IEEE TPAMI 2018, through 2023-2025 follow-ups) reconstructs recognizable face images from embeddings alone, with up to ~98% success even against "privacy-enhanced" embeddings. A public index of raw embeddings is functionally a public index of reconstructable faces.
- **The EDPB's Opinion 11/2024 rejected exactly this shape of design**: centralized/shared storage of biometric templates that isn't keyed solely to the subject herself is not GDPR-compatible, regardless of surrounding safeguards — and this project is Sweden-based, squarely inside GDPR's scope, not a hypothetical edge case.
- **Publishing a network-wide index is also the specific act most likely to end GDPR's household/personal-activity exemption** this project otherwise likely benefits from today (CJEU Lindqvist/Rynes: the exemption doesn't survive data becoming "accessible to an indefinite number of people").

**Revised approach**: never let a decrypted/reconstructable embedding leave its subject's own device or land in any shared/published index at all. Cross-network matching, if ever built, has to happen such that only the searching user's own device ever sees a comparison result — mirroring the EDPB's accepted "subject-device or subject-keyed-only" pattern, not a shared-index pattern. The cryptographic tool that would do this properly — homomorphic encryption or secure multiparty computation, comparing two encrypted embeddings without ever decrypting either — is real, active, peer-reviewed research with genuine server-class speed, but no source found tests it on Pi-class (~1GB RAM) hardware. Treat this feature as **on hold pending that maturing**, not as a solved design with an implementation detail left open.

## Status

Paper design, 2026-07-28/29, security-researched 2026-07-29. Not built, not scheduled — Pillar 1/2 per [../VISION.md](../VISION.md)'s reaffirmed scope. The network/consensus mechanism (DHT/IPFS — see [TODO.md](TODO.md), IPFS itself ruled out for Pi-class hardware 2026-07-29) and the marketplace idea remain open threads; the face-matching privacy question above is resolved to a "not yet, here's why" answer, not a remaining unknown.
