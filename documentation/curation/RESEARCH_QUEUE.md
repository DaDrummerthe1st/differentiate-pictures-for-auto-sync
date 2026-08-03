# Research menu — cherry-pick one, no forced order

Opened 2026-08-02, corrected 2026-08-03: [DETECTORS.md](DETECTORS.md)'s full catalog and
[TODO.md](TODO.md)'s full open-items list are both too much to hold in one session at once. This file
is the fix, refined per Joakim's own correction — **not a prioritized sequence**, just "these are
things we can do," each small enough for one session, picked freely rather than worked in a fixed
order. TODO.md stays as the durable record of *why* each item exists and any decisions already made;
this file is purely the menu.

## Menu

- **VPS hardware audit follow-up** — done 2026-08-03 (see TODO.md's VPS section: specs recorded,
  "Hub Europe" confirmed as Lauterbourg, France). Remaining: nothing blocking, this item is closed.
- **A build plan** — nothing in curation/ is a numbered, TDD-able roadmap yet, only theory/catalog.
  [../photo-server/TODO.md](../photo-server/TODO.md)'s phased format (one numbered step per session, a
  failing test then minimal code, a Security line, human checkpoints) is the precedent to follow once
  detector picks are stable enough to build against.
- **License re-verification pass** over every pick already in DETECTORS.md (object detection, face
  detection/recognition/emotion, NSFW, CLIP embedding, local LLM) — a fresh, independent check against
  the resolved MIT/Apache-2.0-only bar, not a re-trust of this session's own claims.
- **Animal detection/species + pet identity matching** (DETECTORS.md area C) — same crop-then-embed
  pattern as face recognition, per ARCHITECTURE.md's two-embedding-spaces note.
- **Human action/pose recognition** (DETECTORS.md area J) — new, not started at all.
- **Object-detection timing benchmark** — real numbers on the i5-650 or this VPS, not the research
  pass's estimates from faster reference hardware; see TODO.md's benchmarking note.
- **Group/co-presence detection**; **landmark/place recognition** — both queued, neither started.
- **Privacy reads** (not model picks) for age/gender estimation and OCR/text-in-frame, before either
  becomes a research item.
- **Image captioning**; **EXIF-derived human-friendly time labels** (no model needed, cheap); confirm
  weather-at-capture is excluded rather than researched (closed-by-default conflict, likely moot).
- **"Best shot"/attractiveness scoring** (DETECTORS.md area A) — ethically flagged, needs a conscious
  read before it's a plain model pick, same treatment as age/gender. Confirmed 2026-08-03: this menu
  itself is where Joakim wants ideas like this noted ("the approvement-bank") — already correctly
  placed, nothing further needed to file it right.
- **HW-central-record consolidation** — queued behind the `workstation` repo's own concurrent session;
  see TODO.md. Not pickable until that repo is free.

## Status

Corrected 2026-08-03 from an earlier single-"up next"-item design — Joakim explicitly didn't want a
forced sequence. Add items as new areas come up; remove/mark done as items resolve.
