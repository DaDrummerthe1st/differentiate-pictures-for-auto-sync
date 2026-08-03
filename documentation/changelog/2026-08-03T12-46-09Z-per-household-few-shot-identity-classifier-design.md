# Design a per-household few-shot identity classifier for pet/person identity matching

Follow-on from this session's animal-species research: rather than accepting the "no confident pretrained pick" verdict for pet identity matching, Joakim proposed each household train its own tiny classifier from its own bounding-box labels (Fido, Pluto, Snappy) instead of relying on any generic re-id model. Written up in ARCHITECTURE.md: a frozen embedding (CLIP crop-embedding for animals, MobileFaceNet for people) plus a cheap per-household classifier (nearest-neighbor baseline, upgrading to a linear probe as labels accumulate) — no new model, seconds of CPU time to (re)fit. Confirmed to generalize to both people and animals.

Also resolved/flagged along the way:
- A gamified, bounded labeling session ("five minutes to spare") is the bootstrap/cold-start mechanism — specced at vision-level in tags/UX_FLOWS.md's new section.
- Cross-household reuse ("user1 has photos of user2's dog/spouse") split into two problems: consent (resolved as policy — opt-in per entity, per household) and mechanism (deferred to distributed-sync's V2/V3 work, not designed here).
- Mislabeling/false-identification risk on people (a private label could be exported/shared and presented as a verified identification) — flagged as an open privacy item for a future session, same treatment as the existing age/gender and OCR-in-frame flags, not resolved now.

DETECTORS.md area C and RESEARCH_QUEUE.md updated to point at the resolved design instead of the superseded "caveated CLIP fallback" framing. GLOSSARY.md gets few-shot learning and linear probe entries.

- **Doc size**: +~5,800 chars (net, across ARCHITECTURE.md, DETECTORS.md, RESEARCH_QUEUE.md, UX_FLOWS.md, GLOSSARY.md).
