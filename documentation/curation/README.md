# documentation/curation/

Cross-cutting, like [tags/](../tags/README.md) — not a feature folder tied to one branch. This is
VISION.md Pillar 2's other two legs: automated analysis (on-device/server-side inference that
*produces* tags) and "the system suggests photos to remove" (the reasoning layer that *acts* on
tags once they exist). [tags/](../tags/README.md) owns what a tag means; this folder owns how a
tag gets proposed automatically, and what happens next.

| File | What's there |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | The three-layer model: detectors, the embedding/index store, the Curator orchestrator. Start here. |
| [IDENTITY_MATCHING.md](IDENTITY_MATCHING.md) | Usage-intent scoring and identity matching — the per-household few-shot classifier, cross-household linking, mislabeling risk. Split out of ARCHITECTURE.md 2026-08-05 once it grew too large to read as one file. |
| [DETECTORS.md](DETECTORS.md) | Catalog of detection/analysis areas to investigate (blur, faces, animals, places, feelings, burst-duplicates, and more) — breadth-first, one area researched at a time in future sessions, not a locked model matrix. |
| [RESEARCH_QUEUE.md](RESEARCH_QUEUE.md) | **Start here for "what's next"** — a one-item-at-a-time pointer, so a session doesn't have to hold the whole catalog/TODO at once. |
| [TODO.md](TODO.md) | Open items, first TDD-able test steps — the durable why/detail behind each queue item. |

## Why this exists, why now

Opened 2026-08-02 (branch `curation`), prompted by a concrete design question: how does the system
actually get from "a folder of photos" to "I think you'd like to remove these 25 because they were
all blurry," explain that suggestion in terms a user can correct, and use her correction to improve
the next suggestion — not just apply the 12-category taxonomy by hand. See ARCHITECTURE.md for the
full reasoning; short version, explained in chat that session: this is an **embeddings + vector
database** problem (pgvector, already named in [../VISION.md](../VISION.md)) layered under a
reasoning/explanation step, not a single "AI" doing everything at once.

## Scope and constraints inherited, not re-derived here

- **Closed-by-default, no cloud APIs** ([../policies/POLICY.md](../policies/POLICY.md)): every model
  considered here must be open-weight and run entirely locally. Cloud vision APIs (Rekognition,
  Google Vision, Azure, Clarifai, etc.) are disqualified regardless of quality.
- **Resource efficiency is a hard constraint** ([../policies/POLICY.md](../policies/POLICY.md)):
  CPU-only near-term (the photo-server host, see [../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)),
  with an eye toward the eventual Raspberry Pi 3 stress-test target
  ([../photo-server/TODO.md](../photo-server/TODO.md)'s "Raised 2026-07-29" section).
- **On-device phone inference stays the long-term Pillar 2 architecture**
  ([../VISION.md](../VISION.md)) — unaffected by this folder. This folder's near-term design targets
  the V1 rollout note ("also runs and saves AI model output on every picture") which is concretely
  server-side, since no phone app shell exists yet. Confirmed with Joakim 2026-08-02, not assumed.
- **Motivated tagging, not silent automation** ([../VISION.md](../VISION.md) Pillar 2's design
  principle): every automated suggestion this folder designs must be shown to the user for
  review/confirmation, never applied silently — applies to curation suggestions exactly as it
  already applies to manual/detector tags.

## Status

Design-only, opened 2026-08-02. No schema migration, no endpoints, no model actually integrated yet.
See [TODO.md](TODO.md) for the first real test step. **2026-08-05**: ARCHITECTURE.md split (it had grown
to ~30K characters) — usage-intent scoring and identity matching moved to the new
[IDENTITY_MATCHING.md](IDENTITY_MATCHING.md). Forward-effectiveness win: a session that only needs the
identity-matching/scoring design no longer reads the full pipeline/Curator explanation to get there,
and vice versa — same reasoning as [tags/README.md](../tags/README.md)'s own split, applied here once
this folder hit the same size problem.
