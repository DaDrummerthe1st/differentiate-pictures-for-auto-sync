# Research queue — one item at a time

Raised 2026-08-03: [DETECTORS.md](DETECTORS.md)'s full catalog and [TODO.md](TODO.md)'s full open-items
list are both too much to hold in one session at once. This file is the fix — a session opening
curation/ work should read **only "Up next" below**, not the whole catalog/TODO. Pop one item, do it,
move the next one up, done. TODO.md stays as the durable record of *why* each item exists and any
decisions made; this file is purely the queue order.

## Up next

**VPS hardware audit + EU data-residency verification.** Joakim's VPS: `161.97.174.16`, a Contabo
service. See [TODO.md](TODO.md)'s VPS section for what's already confirmed (RIPE registration →
Germany) vs. what still needs Joakim to run the copyable commands there himself and report back.

## Also a real candidate for "next", not yet ordered against the above

**A build plan** — raised 2026-08-03: nothing in curation/ is a numbered, TDD-able roadmap yet, only
theory/catalog. [../photo-server/TODO.md](../photo-server/TODO.md)'s phased format (one numbered step
per session, a failing test then minimal code, a Security line, human checkpoints) is the precedent to
follow once detector picks are stable enough to build against — needs its own session, deliberately
not drafted inline here to avoid repeating this session's own "too big at once" mistake. Joakim should
say whether this or the VPS item goes first.

## Then, roughly in this order (re-order freely, this isn't a commitment)

1. License re-verification pass over every pick already in DETECTORS.md (object detection, face
   detection/recognition/emotion, NSFW, CLIP embedding, local LLM) — a fresh, independent check
   against the now-resolved MIT/Apache-2.0-only bar (see TODO.md), not a re-trust of this session's
   own claims.
2. Animal detection/species + pet identity matching (DETECTORS.md area C) — same crop-then-embed
   pattern as face recognition, per ARCHITECTURE.md's two-embedding-spaces note.
3. Human action/pose recognition (DETECTORS.md area J) — new, not started at all.
4. Approx CPU time per photo for the object-detection pick (real benchmark, not an estimate) — needs
   Joakim to actually run it on the i5-650 or the VPS once picked; see TODO.md's benchmarking note.
5. Group/co-presence detection; landmark/place recognition.
6. Privacy reads (not model picks) for age/gender estimation and OCR/text-in-frame, before either
   becomes a research item.
7. Image captioning; EXIF-derived human-friendly time labels (no model needed, cheap); confirm
   weather-at-capture is excluded rather than researched (closed-by-default conflict, likely moot).
8. HW-central-record consolidation — queued behind the `workstation` repo's own concurrent session;
   see TODO.md.

## Status

Opened 2026-08-03. Update "Up next" every time an item is picked up or finished — this file should
never show more than one active item at a time.
