# Metadata privacy under the DFS — paper design, not built

Scope: Pillar 1/2 per [../VISION.md](../VISION.md)'s reaffirmed scope, paper only. Extends [OWNERSHIP.md](OWNERSHIP.md)'s strict/leased/free tiers to the *metadata* (tags/entities) describing a photo, not just the photo's bytes — partially answering [TODO.md](TODO.md)'s open "where does metadata live" question. Which network mechanism actually carries this metadata (DHT vs. blockchain, and the "sell photos through the network" marketplace idea's implications) is still under active research — see [TODO.md](TODO.md); the exposure-boundary theory below doesn't depend on which mechanism wins that question.

## Raw tag data vs. aggregate/derived signal — two different exposure classes

[../tags/TAXONOMY.md](../tags/TAXONOMY.md) already separates tag *visibility* (private/shareable) from photo *ownership* terms — a free photo can still carry a private tag. This extends that same separation to the network layer: a photo's strict/leased/free tier governs whether its **bytes** replicate; it should never, by itself, decide whether the **names of people in it** become network-visible. Conflating the two — "this photo is free, therefore its tags are public" — would leak person-identifying data ([../security/THREATS.md](../security/THREATS.md) #1, #4) as a side effect of a redistribution decision, not a privacy one.

- **Raw tag/entity content** (a person's name, "Dad", a relationship link) stays owner-controlled regardless of the photo's own tier.
- **Aggregate/derived signal** — embeddings, usage counts (`downloaded_at`/`download_count`, [../tags/SCHEMA.md](../tags/SCHEMA.md)) — is the layer [../VISION.md](../VISION.md) Pillar 2 already wants shared network-wide ("learned globally across the network"). This is the real candidate for open publication: an anonymous index of embeddings and engagement counts, never attached to whose face/name they represent.

## Bounding boxes public, names private — feasible, with one caveat

`tag_references.bounding_box` ([../tags/SCHEMA.md](../tags/SCHEMA.md)) is pixel geometry, stored independently of `reference_value` (the entity it names). Publishing box geometry without the entity link is straightforward — it says "a detectable region existed here," not whose. This genuinely stops *automated* cross-photo linking: an algorithm can't assemble "every photo of Dad" from public data if the entity id never leaves the owner's own node.

**What it doesn't stop**: a human looking at an already-public (free-tier) photo can still visually recognize a face, box or no box, name or no name. The privacy win here is "stops automated re-identification at scale," not "stops a viewer who already recognizes the person."

## Private, per-user cross-network face matching

Raised 2026-07-28: a user wants to find more photos of someone she already has a private reference for (e.g. "Dad") — searching not just her own tagged photos but the wider network's free/leased-tier photos too, via her own on-device face-embedding model, without that search or its results ever becoming visible to anyone else.

Sketch: a public, anonymous index of face-embedding vectors (photo/region pointer + embedding, no name/entity attached) for free/leased-tier photos, produced by the same on-device detection pass ([../VISION.md](../VISION.md) Pillar 2). A user's client computes similarity between her own **private** reference embedding (built from her own tagging) and that public index, entirely client-side — no query or result ever leaves her device or gets logged network-wide. Elegant in principle, but embeddings are themselves biometric-adjacent data (same category as [../security/THREATS.md](../security/THREATS.md) #1) reachable from hardware the photo's subject doesn't control — this is exactly [../security/TODO.md](../security/TODO.md) item 6's open question, now with a second concrete motivating use case. Folded into that item's scope, not treated separately — see that file.

## Status

Paper design, 2026-07-28/29. Not built, not scheduled — Pillar 1/2 per [../VISION.md](../VISION.md)'s reaffirmed scope. The network/consensus mechanism and the marketplace idea are open research threads — see [TODO.md](TODO.md).
