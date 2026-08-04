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
| "Best shot" selection among near-duplicates (e.g. picking a profile-photo candidate from a burst of selfies) | Gaze/eye-openness, attractiveness/appeal scoring | Raised 2026-08-03 — genuinely harder than pass/fail quality; some overlap with eyes-closed/blink above, but "attractiveness scoring" specifically is a real, separate research area | queued — **ethically flagged, not just technically queued**: automated attractiveness scoring risks encoding/amplifying biased beauty standards; needs the same conscious-call treatment as age/gender estimation's privacy flag above, not a plain model pick |

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
| Animal detection/species | Presence + rough species (dog, cat, bird...) | Feeds the animal entity category, [../tags/TAXONOMY.md](../tags/TAXONOMY.md) | researched |
| Pet identity matching | Which specific pet (same idea as face recognition, animal-flavoured) | The literal "same dog" example | researched — no pretrained model fits, resolved instead via a per-household trained classifier, see below |

**Picks (researched 2026-08-03)**: **animal presence/coarse species** — no new model needed: area
D's already-picked NanoDet-Plus (Apache-2.0) is trained on COCO's 80 classes, which already
includes 10 animal categories (bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe) —
zero added cost, same detector pass that finds every other object. **Fine-grained species**
(2000+ taxa, e.g. actual species/breed beyond COCO's coarse buckets) — **Google SpeciesNet
(Apache-2.0)** is the pick if that finer granularity is ever wanted: EfficientNetV2-M backbone
(~55M params, ~200MB fp32), JSON output with species-level label + confidence + taxonomic rollup
when confidence is low, CPU-runnable (no GPU required, just slower) — the heaviest single model
considered across any DETECTORS.md category so far (no ONNX export shipped either, would need a
standard torch→onnx conversion), so treat as an optional add-on once coarse COCO-level species
buckets prove insufficient, not a pipeline default. **Pet identity matching has no turnkey pick**:
the two leading open animal re-identification options were both excluded — MegaDescriptor/WildFusion
(the [WildlifeDatasets](https://github.com/WildlifeDatasets/wildlife-datasets) toolkit) on three
independent grounds (repo AGPL-3.0, the model weights themselves CC-BY-NC-4.0 non-commercial, and
228.8M params/swin-large too heavy regardless of licensing); DogFaceNet is MIT-licensed but ships
no pretrained weights at all, so using it would mean training from scratch. **Pragmatic fallback,
not a confident pick**: reuse the already-loaded OpenCLIP ViT-B/32 embedding (MIT, area H) on the
cropped animal-detection bounding box — the same crop-then-embed pattern
[ARCHITECTURE.md](ARCHITECTURE.md) already uses for face recognition, zero new model to load. Real
caveat, not hidden: recent research (CLIP-AFIR, CARE) treats raw off-the-shelf CLIP embeddings as
explicitly under-adapted to fine-grained instance-level re-identification without few-shot
fine-tuning — expect this fallback to work less reliably than face recognition's dedicated
MobileFaceNet embedding, and revisit if a genuinely permissively-licensed, lightweight, pretrained
animal re-id model appears later (an active research area — CARE, CLIP-AFIR, and NeurIPS's "Toward
Re-Identifying Any Animal" are all 2023-2026 work). Full survey, every candidate considered, and
the full source list: `2026-08-03-animal-species-and-pet-identity-matching-survey.md` in the
`research-findings` repo.

**Actual resolution, same day**: rather than accepting the caveated raw-CLIP fallback above as the
answer, Joakim proposed each household train its own tiny classifier on the labels it provides
("Fido, Pluto, Snappy the bird") instead of relying on any pretrained re-id model — a design that
sidesteps this section's whole "no confident pick" problem, since it needs no new model at all (just
a small classifier trained on top of the embedding already loaded). Full mechanism, the gamified
labeling-session UX that bootstraps it, cross-household reuse, and a flagged mislabeling/liability
risk on people: [ARCHITECTURE.md](ARCHITECTURE.md)'s "Per-household few-shot identity classifier"
section — not duplicated here.

## D. Objects and places

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| General object detection | Recurring things — a motorcycle, a boat, furniture | Feeds the objects entity category | researched |
| Scene/venue classification | Beach, mountains, indoor/outdoor, ski resort | The literal "my countryside" example; also feeds the places category | researched |
| Landmark/place recognition | A *specific* named place, not just a kind of place | [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s "specific" place sub-case | queued |
| Text/OCR in-frame | Signs, documents, whiteboards accidentally captured | Real privacy angle — a photographed ID card or letter is sensitive content hiding inside an otherwise ordinary photo | queued, privacy-flagged — mechanism sketched 2026-08-04, no model pick yet |
| Number plate / vehicle registration (ANPR) | A car's license plate, incidentally in-frame | Raised 2026-08-05: a distinct sub-case, not just another OCR string — a plate is personal data (resolves to a registered keeper via the national vehicle registry) even though it isn't GDPR "special category" biometric data. **Corrected same day, per Joakim**: no Swedish law bars a private individual from looking a plate up (the registry is deliberately open), and this project *builds a detection capability into the codebase* — it isn't the GDPR controller for what an independent self-hosting user does with her own instance on her own data, same non-liability logic as a camera manufacturer isn't the controller for what its owner photographs (this project's architecture makes that distinction real, not just asserted — each deployment is closed-by-default, single-controller, no central collection by Joakim, [../policies/POLICY.md](../policies/POLICY.md)). The DPIA-relevant point that remains is narrower and controller-side, not a legality concern: *for whichever party ends up as controller of a given instance*, GDPR's household exemption ([../GLOSSARY.md](../GLOSSARY.md)) is the first and most relevant lens, same as everywhere else in this project — plate detection for one's own private/family photos plausibly never leaves that exemption in practice. | queued, no legality concern — controller/exemption nuance noted for whoever operates a given instance |

**Picks (researched 2026-08-02, license bar tightened 2026-08-03 — see below)**: **object detection**
— **NanoDet-Plus (Apache-2.0)** is the pick, full stop; YOLO26n is **excluded**, not just flagged —
AGPL-3.0's network-use clause is a real obligation once this project reaches VISION.md's own V2/V3
multi-household/commercialize phases, not a low risk specific to today's private single-household
use (see [ARCHITECTURE.md](ARCHITECTURE.md)'s existing prototype note: full YOLOv3 is the wrong
weight class either way, ~236MB vs. NanoDet-Plus's single-digit MB). **Scene/venue classification** — don't add a separate model at all: reuse the CLIP-family embedding already computed for area H via zero-shot classification (cosine similarity against text prompts like "a photo of a beach") rather than a dedicated Places365 classifier — zero added footprint, and new scene categories are just new text prompts instead of retraining.

## E. Cross-photo / batch-relational (not a single-photo detector)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Burst/near-duplicate clustering | Many shots at ~the same timestamp | Joakim's own example this session — "many pictures on the same timestamp" | researched (mechanism, see below) |
| Perceptual hashing (pHash/dHash) | Near-identical images even if resized/re-saved | The general mechanism behind burst clustering; [../photo-server/DEFERRED.md](../photo-server/DEFERRED.md) already deferred this once ("quality-of-life, not required") — worth revisiting now that curation, not just dedupe, wants it | researched |
| Panorama/sequence detection | Photos meant to be stitched together | Narrower case of the above | queued |

**Re-upload/crop scenarios, clarified 2026-08-03**: three distinct cases, three different mechanisms — (1) the *exact same bytes* re-uploaded under a different filename is already caught by the planned content-addressed storage design ([../upload-and-share/UPLOAD.md](../upload-and-share/UPLOAD.md), designed not built) — identical bytes always resolve to the same stored file regardless of the filename used at upload, automatically. (2) The *same photo, re-encoded* (re-saved by a different app, slightly different compression, so bytes differ but it's visually identical) is what pHash below is actually for. (3) A **cropped** version is the hard case — pHash is explicitly brittle against crops (noted below), so this falls to the CLIP embedding fallback instead; a tight crop of the same subject will likely, but not certainly, land close enough in embedding space to be flagged as related — untested, not guaranteed, worth a real check once a model is wired up rather than assumed. In all three cases the *action* is the same: surface as a review batch ("these look like the same/related photo — keep one, some, or all?"), same pattern as the worked blurry-cluster example in [ARCHITECTURE.md](ARCHITECTURE.md), never auto-deleted.

**Picks (researched 2026-08-02)**: of the three classic hash algorithms (aHash/dHash/pHash), **pHash** (DCT-based, keeps only low-frequency coefficients) is the most robust to mild recompression/resizing — meaningfully better than plain sha256 for this, since sha256 only catches byte-identical files and misses the extremely common "two frames from the same burst, resaved" case. All three are brittle against crops/flips/rotations though. Recommended design: a two-tier filter — pHash as a cheap (sub-millisecond) first pass for near-identical burst frames, falling back to the area-H CLIP embedding's cosine similarity for genuinely "related but reframed" photos (more expensive, but already computed for search anyway).

## F. Privacy and safety (already partly flagged elsewhere)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Nudity/NSFW detection | Explicit content | Already an open item, [../tags/TODO.md](../tags/TODO.md) — forces the privacy category's automatic-private behaviour | researched |
| CSAM perceptual-hash matching | Known illegal content | Already the stated moderation mechanism, [../policies/POLICY.md](../policies/POLICY.md) — a blocklist match, not a learned classifier | queued (mechanism already decided, not a research item so much as an implementation one) |

**Pick (researched 2026-08-02, license bar tightened 2026-08-03)**: **Open-NSFW2 is the pick**
(permissive BSD-lineage license), not NudeNet v3 — NudeNet is **excluded**: AGPL-3.0, same reasoning
as area D's YOLO26n exclusion above. Real trade-off named, not hidden: Open-NSFW2 only returns a
single coarse NSFW probability, not NudeNet's 18-class body-part-level output — less granular, but
still sufficient to gate the privacy category's automatic-private behavior (a binary "flag for
review" is all that decision needs).

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

**Pick (researched 2026-08-02, license bar tightened 2026-08-03)**: **OpenCLIP ViT-B/32 (MIT) is the
pick** — MobileCLIP2-S0 is **excluded**: not AGPL, but Apple's own Sample Code License is a
non-standard, restrictive license, the same category of problem as a copyleft license for a project
that wants unrestricted commercial use. OpenCLIP ViT-B/32 also happens to have the most mature CPU/
ONNX deployment path of anything surveyed, so nothing is given up by excluding MobileCLIP2 beyond its
edge-latency advantage (3-15ms vs. OpenCLIP's larger footprint) — acceptable given V1 targets a server,
not an edge device yet. SigLIP (Apache-2.0) remains a fully-open second option if OpenCLIP's accuracy
disappoints in practice.

**OCR-in-frame → privacy tag, mechanism sketched (not a model pick), raised 2026-08-04**: the shape
Joakim asked for — extracted text ending up as a per-photo tag a sharing decision can act on, not just
a detection sitting unused. Reuses every mechanism [../tags/](../tags/README.md) already designed,
adding only the OCR detector itself and a text-pattern step: (1) an OCR detector outputs
`{text, bounding_box, confidence}` per detected text region, same output shape as every other
detector here; (2) a lightweight **pattern-match** heuristic (regexes — Swedish personnummer format,
email, phone number, street-address-like strings; no cloud PII-detection API, consistent with
[../policies/POLICY.md](../policies/POLICY.md)'s closed-by-default rule) flags candidate regions, not a
model — cheap and explainable, same bar as area A's blur/exposure picks; (3) a flagged region surfaces
Joakim's own proposed confirm prompt — *"Is this information so vital that you wouldn't want anybody
else to know about it? Then let's blur it"* — never auto-applied, per this project's standing
motivated-tagging principle ([README.md](README.md)); (4) confirming creates an ordinary
**privacy**-category tag ([../tags/TAXONOMY.md](../tags/TAXONOMY.md)) scoped to that bounding box,
which forces `visibility=private` and flows straight into the already-designed blur-preview sharing
review ([../tags/UX_FLOWS.md](../tags/UX_FLOWS.md)) — no new sharing mechanism needed. **Not resolved**:
which OCR model/engine (a real pick needs its own research pass, same bar as every other area — MIT/
Apache-2.0, CPU-only, self-hosted), and the "privacy read" [RESEARCH_QUEUE.md](RESEARCH_QUEUE.md)
already flags as needed before this becomes a model pick.

## I. Behavioral / usage signals (not a detector — derived from user actions)

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Share/folderization/repeat-view/search-engagement frequency | How much a photo/entity actually gets used | [ARCHITECTURE.md](ARCHITECTURE.md)'s usage-intent score, re-weighted 2026-08-03 — these outrank downloads; fields to add, not yet in [../tags/SCHEMA.md](../tags/SCHEMA.md) | queued |
| Download frequency | Same idea, lower-value signal | Fields already reserved ([../tags/SCHEMA.md](../tags/SCHEMA.md)) but demoted per ARCHITECTURE.md's 2026-08-03 note — kept as one input, not the leading one | queued |
| Explicit corrections (kept/excluded/confirmed) | User overrides of an automated suggestion | Same score, higher-confidence input | queued |
| Undo events | A suggestion the user reversed | Ambiguous signal (mistake vs. genuine uncertainty) — see [ARCHITECTURE.md](ARCHITECTURE.md)'s Curator section, not resolved | queued |

## J. Actions — what people are doing

Raised 2026-08-03: distinct from area B's *who* and the existing activity/occasion tag category's
*occasion* (skiing, a birthday party — an event-level label) — this is per-person action/pose within
a single photo (waving, hugging, jumping, sitting), a finer grain than either. Not researched.

| Area | What it detects | Why it matters | Status |
| --- | --- | --- | --- |
| Human action/pose recognition | What a specific person is doing in-frame | New dimension Joakim asked to add; distinct from occasion-level activity tags already in [../tags/TAXONOMY.md](../tags/TAXONOMY.md) | queued |

## Also flagged, not a detection area

- **Local LLM for the Curator's conversational layer** — not a detector, a narration layer; see
  [ARCHITECTURE.md](ARCHITECTURE.md). **Researched 2026-08-02, lower priority**: pick is **Qwen2.5
  1.5B-Instruct** (Apache-2.0, ~1.5-2GB RAM at Q4 quantization via llama.cpp, best size/quality/license
  balance surveyed). Phi-3.5-mini (MIT, ~3GB) is a stronger-reasoning fallback if 1.5B proves too
  weak. Llama 3.2 1B and Gemma 3 1B were also surveyed but both carry custom, non-OSI-approved
  licenses (Meta's Community License, Google's Gemma license) — Qwen/Phi avoid that ambiguity.
- **Video handling** — this project also indexes movie clips ([../picture-handling/README.md](../picture-handling/README.md)), not just stills. Every visual area above needs a "what do we do for video" answer eventually (frame sampling, at minimum) — not researched at all yet, flagged so its absence is a decision.
- **Reverse OCR search — "feed me text you want protected, I'll flag/blur every photo containing it," raised 2026-08-04**: the inverse of the OCR-in-frame idea above — instead of the system surfacing text it found, the user supplies text she cares about (an address, an ID number, a name) and the system matches it against already-extracted OCR text across her whole library. **Correction to Joakim's own framing when he raised this**: this does *not* need an LLM/conversational service at all, despite reading like one — once OCR text is extracted and stored per photo (same index layer as every other detector output, [ARCHITECTURE.md](ARCHITECTURE.md)), matching a user-supplied string list against it is a plain exact/fuzzy-string database query, the same shape as the Curator's existing no-generation worked examples ([ARCHITECTURE.md](ARCHITECTURE.md)). Genuinely speculative — no functionality behind it today, blocked on the OCR detector above existing first; flagged as an idea, not queued as a build item.

## Status

Opened 2026-08-02, alongside [ARCHITECTURE.md](ARCHITECTURE.md). This is a catalog, deliberately not
exhaustive-forever — add rows as new areas come up. **Going forward, one area per session** (or a
small tightly-related cluster, like blur+exposure+noise), not the whole table at once — this
session's "researched" rows (blur/exposure/monochrome, face detection/recognition/emotion, object
detection, scene classification, NSFW, CLIP embeddings, perceptual hashing, the local-LLM aside) are
a one-time head start from a background pass launched before the scope narrowed to cataloging, not
the intended future cadence. **License bar resolved 2026-08-03**: MIT/Apache-2.0 only, given
VISION.md's own V2/V3 multi-household/commercialize plan makes AGPL's network-use clause a real
future obligation, not a low risk — every pick above now reflects that (NanoDet-Plus, Open-NSFW2,
OpenCLIP ViT-B/32), with the previously-flagged AGPL/restrictive options explicitly excluded rather
than offered as accuracy/latency-driven alternatives. A fresh, independent license-verification pass
over all of these is still queued (this session's own claims shouldn't be trusted without a
re-check) — see [RESEARCH_QUEUE.md](RESEARCH_QUEUE.md). **Animals (area C) researched 2026-08-03** —
coarse species reuses the existing object detector at zero cost, fine-grained species has a pick
(SpeciesNet) but is an optional add-on, and pet identity matching has no confident pick, only a
caveated fallback — see area C above and the full survey in the `research-findings` repo. See
[TODO.md](TODO.md) for the still-queued areas (landmarks, OCR, age/gender, group/co-presence,
EXIF-derived time labels, image captioning, usage signals, actions/pose). **2026-08-04**: OCR-in-frame
got a UX mechanism sketch (still no model pick) and a speculative reverse-search idea was added under
"Also flagged" — see area D above.
