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
- **Animal detection/species + pet identity matching** (DETECTORS.md area C) — done 2026-08-03: coarse
  species is free (reuses the existing object detector's COCO classes), fine-grained species has an
  optional pick (SpeciesNet). Pet identity matching has no pretrained model under the MIT/Apache-2.0
  bar, resolved instead by a per-household few-shot classifier trained on the user's own labels
  (generalizes to people too) — see IDENTITY_MATCHING.md's "Per-household few-shot identity classifier"
  section and the research-findings repo's 2026-08-03 entry for the full survey behind the "no
  pretrained pick" finding. Remaining: nothing blocking, this item is closed.
- **Mislabeling/false-identification privacy risk on people** — flagged 2026-08-03, alongside the
  per-household identity classifier above: nothing stops a user mislabeling a face with a real
  person's name, and such a private label could be exported/shared and presented as though it were a
  verified identification (e.g. wrongly placing someone at a real event). Same treatment as the
  existing age/gender and OCR-in-frame privacy flags — needs a conscious read before a safeguard is
  designed, not a plain model/UX pick. See IDENTITY_MATCHING.md's flagged note.
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
- **Bring-your-own identity model, compared against the per-household classifier** — raised 2026-08-04
  (Joakim asked about contributing his own pretrained person/animal-detection model). Not designed:
  what a fair comparison against the existing per-household few-shot classifier
  ([IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)) would even measure, whether it replaces or just supplements the
  built-in pipeline, and the accept-format constraint already flagged as a real risk
  ([../security/THREATS.md](../security/THREATS.md) #12 — ONNX/safetensors only, never raw pickle/
  `.pt`, since a model file is executable-code-adjacent, not inert data like a photo).
- **OCR-in-frame — real model pick**, now that the UX mechanism is sketched ([DETECTORS.md](DETECTORS.md)
  area D, 2026-08-04): still needs its own research pass (candidate OCR engines, MIT/Apache-2.0 bar,
  CPU-only) and the privacy read this menu already flags as a prerequisite.

## Status

Corrected 2026-08-03 from an earlier single-"up next"-item design — Joakim explicitly didn't want a
forced sequence. Add items as new areas come up; remove/mark done as items resolve.
