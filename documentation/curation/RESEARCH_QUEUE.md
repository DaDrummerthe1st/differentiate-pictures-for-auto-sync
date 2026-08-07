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
- **A build plan** — started 2026-08-07, Phase 0-1 done (role-based tag visibility, `detector/`
  service skeleton), Phase 2 (the quality trio: blur/exposure/monochrome) is next session's starting
  point. See [TODO.md](TODO.md)'s "Build plan" section for the handoff. Not closed — phases 2-7
  remain.
- **License re-verification pass** — done 2026-08-05: every current DETECTORS.md pick independently
  re-checked against its own LICENSE file/model card, all confirmed; Open-NSFW2's wording tightened
  from "BSD-lineage" to a confirmed MIT pick; one real-but-non-reversing nuance flagged on
  MobileFaceNet's training-data lineage (same InsightFace-format training data as `buffalo_s`, though
  Hailo's own redistribution license carries no restriction). Full table:
  `2026-08-05-license-reverification-and-privacy-reads.md` in the `research-findings` repo. Remaining:
  nothing blocking, this item is closed.
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
- **Human action/pose recognition** (DETECTORS.md area J) — done 2026-08-05: pose-estimation stage
  picked (MediaPipe Pose, Apache-2.0), action-classification stage has no confident pretrained pick
  (every candidate's license traces back to an unverifiable or copyleft-flavored dataset license) —
  resolved to a keypoint-heuristic/self-trained approach instead, same shape of conclusion as area C's
  pet-identity survey. Full survey: `2026-08-05-human-action-pose-recognition-survey.md` in
  `research-findings`. Remaining: nothing blocking, this item is closed.
- **Object-detection timing benchmark** — real numbers on the i5-650 or this VPS, not the research
  pass's estimates from faster reference hardware; see TODO.md's benchmarking note.
- **Group/co-presence detection** — done 2026-08-05: no new model needed, resolved to a query over
  the already-picked face-recognition matches (TAXONOMY.md already defines the category as
  entity-linking only, no bounding box). See DETECTORS.md area B. Remaining: nothing blocking, this
  item is closed.
- **Landmark/place recognition** — still queued, not started.
- **Privacy reads** (not model picks) for age/gender estimation and OCR/text-in-frame — **both done
  2026-08-05**. Age/gender: EDPB Guidelines 3/2019 §80-81 hold that classification without an
  identifying template doesn't trigger GDPR Article 9 on its own — substantially de-risked, now
  unblocked for a plain model-pick pass (DETECTORS.md area B). OCR: text extraction is itself GDPR
  processing before any pattern-match runs, making the already-designed pattern-match step
  load-bearing for data minimization, not just UX — carried into the OCR model-pick item below.
  Full reads: `2026-08-05-license-reverification-and-privacy-reads.md` in `research-findings`.
  Remaining: nothing blocking either read itself, this item is closed. **Age/gender's unblocked
  model pick is also now done, same day**: OpenVINO's `age-gender-recognition-retail-0013`
  (Apache-2.0). Full survey: `2026-08-05-age-gender-estimation-model-survey.md` in
  `research-findings`. See DETECTORS.md area B. OCR's unblocked model pick is a separate menu item,
  below, also now closed.
- **Image captioning** — still queued, not started.
- **EXIF-derived human-friendly time labels** — done 2026-08-05: confirmed no model/research needed,
  a deterministic lookup (solar-position bucketing + hemisphere-aware season labels) — buildable
  whenever the build-plan item is picked up. Remaining: nothing blocking, this item is closed.
- **Weather-at-capture exclusion** — confirmed and closed 2026-08-05: no offline, self-hostable,
  worldwide historical-weather dataset exists at a size compatible with this project's resource-tight
  posture — excluded per closed-by-default, not just "likely." Remaining: nothing blocking, this item
  is closed.
- **"Best shot"/attractiveness scoring** (DETECTORS.md area A) — ethical read **done 2026-08-05**:
  peer-reviewed literature (AAAI AIES, MDPI) confirms the bias risk is real, not hypothetical —
  non-diverse training data skews standards, and models measurably reinforce narrow ("lookism")
  beauty standards. Go/no-go on shipping the feature at all is still Joakim's open design call, not
  resolved by this read. Confirmed 2026-08-03: this menu itself is where Joakim wants ideas like this
  noted ("the approvement-bank") — already correctly placed, nothing further needed to file it right.
- **HW-central-record consolidation** — queued behind the `workstation` repo's own concurrent session;
  see TODO.md. Not pickable until that repo is free.
- **Bring-your-own identity model, compared against the per-household classifier** — raised 2026-08-04
  (Joakim asked about contributing his own pretrained person/animal-detection model). Not designed:
  what a fair comparison against the existing per-household few-shot classifier
  ([IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)) would even measure, whether it replaces or just supplements the
  built-in pipeline, and the accept-format constraint already flagged as a real risk
  ([../security/THREATS.md](../security/THREATS.md) #12 — ONNX/safetensors only, never raw pickle/
  `.pt`, since a model file is executable-code-adjacent, not inert data like a photo).
- **OCR-in-frame — real model pick** — done 2026-08-05: **RapidOCR** (Apache-2.0, ONNX re-export of
  PP-OCR weights) is the pick, specifically avoiding stock PaddleOCR's live ~43GB-RAM CPU-inference
  bug. Runner-up: Tesseract. Full survey: `2026-08-05-ocr-in-frame-engine-survey.md` in
  `research-findings`. See DETECTORS.md area D. Remaining: nothing blocking, this item is closed.

## Status

Corrected 2026-08-03 from an earlier single-"up next"-item design — Joakim explicitly didn't want a
forced sequence. Add items as new areas come up; remove/mark done as items resolve. **2026-08-05**:
six items closed in one session (license re-verification pass; age/gender and OCR privacy reads;
"best shot" ethical read; EXIF-derived time labels; weather-at-capture exclusion) — deliberately
scoped to verification/reads only, not a new detector-area survey, per TODO.md's "one area per
session" cadence. Full writeup: `2026-08-05-license-reverification-and-privacy-reads.md` in the
`research-findings` repo. **2026-08-05 (same day, third pass)**: four more items closed in one
session, per Joakim's explicit go-ahead to research everything that comfortably fits rather than one
area at a time — group/co-presence detection (no new model), age/gender model pick, OCR-in-frame
model pick, and human action/pose recognition (its first research pass ever, area J). Landmark/place
recognition and image captioning remain open, not attempted this session — next candidates for a
future pass. Full surveys: `2026-08-05-ocr-in-frame-engine-survey.md`,
`2026-08-05-age-gender-estimation-model-survey.md`, `2026-08-05-human-action-pose-recognition-survey.md`
in the `research-findings` repo. **2026-08-07**: the "A build plan" item above stopped being purely
theoretical — Phase 0 (role-based tag visibility) and Phase 1 (`detector/` service skeleton) are
built, session scope deliberately narrowed to just those two; TODO.md's "Build plan" section has the
full handoff for Phase 2 onward.
