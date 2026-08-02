# Areas to investigate

A catalog, not a decision — breadth first. Each row is one candidate detection/analysis area a
future session can pick up and research **one at a time**, in a small, self-contained chunk (model
options, resource cost, output shape, a pick) rather than all at once. Deliberately not a locked
model matrix — see [ARCHITECTURE.md](ARCHITECTURE.md) for how any of these plug into the
detector/index/Curator pipeline once picked.

Status values: **queued** (not looked at), **researching** (a background pass from this session's
opening is mid-flight, see Status section below), **researched** (has a real model recommendation,
written up here once done).

## A. Single-photo intrinsic quality

| Area | What it detects | Why it matters (tied to real use cases above) | Status |
| --- | --- | --- | --- |
| Blur / focus | Sharp vs. blurry | The literal "these 25 are all blurry" example | researched |
| Exposure | Over/under-exposed | Same bucket as blur for a "technically bad photo" cluster | researched |
| Monochrome/low-colour | Black-and-white or washed-out ("pocket-shot") | Already named in [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s quality category | researched |
| Noise/grain | High-ISO grain, compression artifacts | Same bucket, another "technically bad" signal | queued |
| Eyes-closed / blink | A face mid-blink | Classic "otherwise good photo, ruined by one detail" flag — a person-level, not whole-photo, quality signal | queued |
| Aesthetic/composition scoring | Rule-of-thirds, framing quality | More subjective/harder; lower priority | queued (NIMA/MobileNet backbone flagged as a future option if wanted — Apache-2.0, ~4M params, &lt;200MB) |

**Picks (researched 2026-08-02)**: no model needed for blur/exposure/monochrome — classic, near-zero-cost techniques cover all three: variance-of-Laplacian for blur (`cv2.Laplacian(...).var()`), a luminance histogram for over/under-exposure, and a near-zero saturation-channel mean for black-and-white. Negligible CPU cost, no license to track, no RAM footprint worth mentioning — the right call given the resource-efficiency constraint, not a placeholder pending a "real" model.

## B. People

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Face detection | Where faces are (box) | Feeds bounding-box tagging, [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md) | researched |
| Face recognition/identity | Which known person (embedding match against `entities`) | The literal "same dog" example, applied to people — "all photos of Dad" | researched |
| Facial expression/emotion | Happy, sad, neutral, etc. | Joakim's own V1 rollout note ("feelings/emotions"), [../VISION.md](../VISION.md) | researched |
| Group/co-presence | Multiple known people together | Feeds the co-presence/group tag category, [../tags/TAXONOMY.md](../tags/TAXONOMY.md) | queued |
| Age/gender estimation | Rough demographic guess | **Flag, not just queue**: this plus a face embedding edges toward GDPR "special category" biometric data — see [../GLOSSARY.md](../GLOSSARY.md)'s "biometric data" entry. Needs a privacy read before research, not just a model pick. | queued, privacy-flagged |

**Picks (researched 2026-08-02)**: **face detection** — YuNet (OpenCV Zoo, Apache-2.0, sub-1MB ONNX, millisecond CPU cost, ships free via OpenCV's built-in `FaceDetectorYN`, already returns 5 landmarks). **Face recognition/embedding** — MobileFaceNet's standalone MIT-licensed ONNX release (~1M params, 128-d embedding) over InsightFace's `buffalo_s` bundle, specifically to sidestep InsightFace's pretrained-weights license (code is MIT, but the weights themselves are non-commercial-research-only per their own policy — a gray area for a private but non-"research" family server, worth a conscious call rather than an assumption). **Emotion** — FER+ (`emotion-ferplus-8`, Apache-2.0, ready-made ONNX file from the ONNX Model Zoo) is the *only* genuinely turnkey pretrained option found in this category; everything else surveyed is research code needing your own training/export.

## C. Animals

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Animal detection/species | Presence + rough species (dog, cat, bird...) | Feeds the animal entity category, [../tags/TAXONOMY.md](../tags/TAXONOMY.md) | queued |
| Pet identity matching | Which specific pet (same idea as face recognition, animal-flavoured) | The literal "same dog" example | queued |

## D. Objects and places

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| General object detection | Recurring things — a motorcycle, a boat, furniture | Feeds the objects entity category | researched |
| Scene/venue classification | Beach, mountains, indoor/outdoor, ski resort | The literal "my countryside" example; also feeds the places category | researched |
| Landmark/place recognition | A *specific* named place, not just a kind of place | [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s "specific" place sub-case | queued |
| Text/OCR in-frame | Signs, documents, whiteboards accidentally captured | Real privacy angle — a photographed ID card or letter is sensitive content hiding inside an otherwise ordinary photo | queued, privacy-flagged |

**Picks (researched 2026-08-02)**: **object detection** — NanoDet-Plus (Apache-2.0, sub-2MB weights, the smallest footprint surveyed) as the default; YOLO26n is a real alternative with materially better accuracy but ships **AGPL-3.0** (a license flag, not disqualifying for a private non-distributed server, but worth a conscious call — see [ARCHITECTURE.md](ARCHITECTURE.md)'s note that the existing prototype's full YOLOv3 is the wrong weight class either way, ~236MB vs. these nano variants' single-digit MB). **Scene/venue classification** — don't add a separate model at all: reuse the CLIP-family embedding already computed for area H via zero-shot classification (cosine similarity against text prompts like "a photo of a beach") rather than a dedicated Places365 classifier — zero added footprint, and new scene categories are just new text prompts instead of retraining.

## E. Cross-photo / batch-relational (not a single-photo detector)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Burst/near-duplicate clustering | Many shots at ~the same timestamp | Joakim's own example this session — "many pictures on the same timestamp" | researched (mechanism, see below) |
| Perceptual hashing (pHash/dHash) | Near-identical images even if resized/re-saved | The general mechanism behind burst clustering; [../photo-server/DEFERRED.md](../photo-server/DEFERRED.md) already deferred this once ("quality-of-life, not required") — worth revisiting now that curation, not just dedupe, wants it | researched |
| Panorama/sequence detection | Photos meant to be stitched together | Narrower case of the above | queued |

**Picks (researched 2026-08-02)**: of the three classic hash algorithms (aHash/dHash/pHash), **pHash** (DCT-based, keeps only low-frequency coefficients) is the most robust to mild recompression/resizing — meaningfully better than plain sha256 for this, since sha256 only catches byte-identical files and misses the extremely common "two frames from the same burst, resaved" case. All three are brittle against crops/flips/rotations though. Recommended design: a two-tier filter — pHash as a cheap (sub-millisecond) first pass for near-identical burst frames, falling back to the area-H CLIP embedding's cosine similarity for genuinely "related but reframed" photos (more expensive, but already computed for search anyway).

## F. Privacy and safety (already partly flagged elsewhere)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Nudity/NSFW detection | Explicit content | Already an open item, [../tags/TODO.md](../tags/TODO.md) — forces the privacy category's automatic-private behaviour | researched |
| CSAM perceptual-hash matching | Known illegal content | Already the stated moderation mechanism, [../policies/POLICY.md](../policies/POLICY.md) — a blocklist match, not a learned classifier | queued (mechanism already decided, not a research item so much as an implementation one) |

**Pick (researched 2026-08-02)**: NudeNet v3 — described in current sources as the only viable fully open-source, CPU-capable nudity detector, with body-part-level output (18 classes, e.g. `FEMALE_GENITALIA_EXPOSED`, each with a box and score) rather than a single coarse score. License flag: **AGPL-3.0** — low practical risk for a private, non-distributed self-hosted tool, but the same conscious-call note as area D's YOLO26n applies. A simpler binary-score fallback (Open-NSFW2, permissive BSD-lineage license, no body-part granularity) exists if AGPL is a hard blocker.

## G. Metadata-derived (non-visual, still automatic)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| EXIF/GPS extraction | Where/when a photo was taken | Already built ([../../prototypes/differentiate_pictures/app/gpsdata.py](../../prototypes/differentiate_pictures/app/gpsdata.py)) | done (pre-existing) |
| Human-friendly time labels | "Golden hour," "winter," from raw EXIF timestamp | Feeds the temporal/seasonal tag category without a vision model at all — cheap, no inference needed | queued |
| Weather at time/place | Sunny, rainy, snowy | Would need a weather API lookup by GPS+timestamp — **likely excluded**: conflicts with closed-by-default/no-cloud-APIs unless a fully offline historical-weather dataset exists; flag, don't assume. | queued, policy-flagged |

## H. Semantic / free-text search backbone

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| CLIP-style joint image-text embedding | A vector letting text queries match photos directly | The literal "show me my countryside" example; the backbone of [ARCHITECTURE.md](ARCHITECTURE.md)'s index layer | researched |
| Image captioning | A free-text description per photo | Could feed full-text search as a fallback/complement to embeddings; heavier than a pure embedding model | queued |

**Pick (researched 2026-08-02)**: **MobileCLIP2-S0** (Apple) is the most edge-optimized option found — an 11.4M-param image encoder purpose-built for 3-15ms edge latency, smallest of every CLIP variant surveyed — but ships under Apple's own **Sample Code License**, a non-standard, restrictive license, not Apache/MIT. If a genuinely permissive license is a hard requirement, **OpenCLIP ViT-B/32** (MIT, 512-d embedding, the most mature CPU/ONNX deployment path of anything surveyed) is the safer default, or **SigLIP** (Apache-2.0, Google) as a competitive, fully-open middle ground. This license choice is a real open decision, not resolved here — flagged in [TODO.md](TODO.md).

## I. Behavioral / usage signals (not a detector — derived from user actions)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Download/view/share frequency | How much a photo/entity actually gets used | [ARCHITECTURE.md](ARCHITECTURE.md)'s usage-intent score; fields already reserved, [../tags/SCHEMA.md](../tags/SCHEMA.md) | queued |
| Explicit corrections (kept/excluded/confirmed) | User overrides of an automated suggestion | Same score, higher-confidence input | queued |

## Also flagged, not a detection area

- **Local LLM for the Curator's conversational layer** — not a detector, a narration layer; see
  [ARCHITECTURE.md](ARCHITECTURE.md). **Researched 2026-08-02, lower priority**: pick is **Qwen2.5
  1.5B-Instruct** (Apache-2.0, ~1.5-2GB RAM at Q4 quantization via llama.cpp, best size/quality/license
  balance surveyed). Phi-3.5-mini (MIT, ~3GB) is a stronger-reasoning fallback if 1.5B proves too
  weak. Llama 3.2 1B and Gemma 3 1B were also surveyed but both carry custom, non-OSI-approved
  licenses (Meta's Community License, Google's Gemma license) — Qwen/Phi avoid that ambiguity.
- **Video handling** — this project also indexes movie clips ([../picture-handling/README.md](../picture-handling/README.md)), not just stills. Every visual area above needs a "what do we do for video" answer eventually (frame sampling, at minimum) — not researched at all yet, flagged so its absence is a decision.

## Status

Opened 2026-08-02, alongside [ARCHITECTURE.md](ARCHITECTURE.md). This is a catalog, deliberately not
exhaustive-forever — add rows as new areas come up. **Going forward, one area per session** (or a
small tightly-related cluster, like blur+exposure+noise), not the whole table at once — this
session's "researched" rows (blur/exposure/monochrome, face detection/recognition/emotion, object
detection, scene classification, NSFW, CLIP embeddings, perceptual hashing, the local-LLM aside) are
a one-time head start from a background pass launched before the scope narrowed to cataloging, not
the intended future cadence. Every pick above still needs an actual license decision where flagged
(AGPL vs. permissive alternatives for object detection and NSFW; Apple's restrictive license vs. MIT/
Apache-2.0 for the CLIP embedding) before real integration — a research pick, not a final choice. See
[TODO.md](TODO.md) for the actual next step and the still-queued areas (animals, landmarks, OCR,
age/gender, group/co-presence, EXIF-derived time labels, image captioning, usage signals).
