# Curation architecture — three layers

How the system gets from "a folder of photos" to a suggestion a user can understand, correct, and
have the correction actually improve the next suggestion. Explained in full in chat, 2026-08-02 —
this file is the durable record of that explanation, not a substitute for it.

## The three layers

```
 photo ──▶ [1] Detectors ──▶ [2] Index (Postgres + pgvector) ◀── query ── [3] The Curator ──▶ user
              (series,          structured tags + embedding                explains, proposes,
              one model          per photo, hybrid search                  incorporates corrections
              loaded once,        (exact filter + nearest-
              streamed over        neighbor similarity)
              the backlog)
```

### 1. Detectors

One narrow, single-purpose lightweight model per task — a blur detector, a face detector, an
object detector, and so on. Each looks at one photo, outputs one structured fact (a score, a box, a
label), and has no memory of any other photo. Run **in series across models, not in series per
photo**: a persistent worker process loads every detector once at startup, then streams the whole
backlog through the fixed pipeline — model-load cost is paid once per run, not once per photo. See
[DETECTORS.md](DETECTORS.md) for the actual model choices.

**Series-of-specialized-models vs. one shared-backbone multi-task model, researched 2026-08-02**:
sharing a backbone across tasks genuinely cuts memory/inference time (the backbone forward pass runs
once, only lightweight per-task heads run after) — but no off-the-shelf model spans this project's
specific task mix, so building one means training a custom multi-head net, a real project of its own,
not a pick. Recommended hybrid instead: treat the CLIP-family embedding
([DETECTORS.md](DETECTORS.md) area H) as the one genuinely shared backbone — compute it once per
photo and reuse it for semantic search, zero-shot scene classification (area D), and near-duplicate/
relatedness ranking (area E), three tasks that are naturally CLIP-embedding-space operations and come
essentially free once the embedding exists. Keep object detection, face detection→embedding, quality
assessment, and NSFW as separate specialized models run in series — each needs fundamentally
different input handling (full-frame spatial output vs. an aligned face crop vs. a different training
distribution entirely) that a shared backbone can't cleanly serve, and on a 2-core/4-thread machine
wall-clock time is dominated by whichever single stage is slowest anyway, not by how many small
models are loaded. A useful side effect: separate models are easy to skip conditionally (no faces
detected → skip face-embedding entirely), which a monolithic multi-task net wouldn't allow as cleanly.

### 2. The index

Not a separate service — one set of columns/tables in the existing Postgres instance (pgvector
extension). Every detector's output, plus a CLIP-style joint image-text embedding, gets stored per
photo. This is what turns isolated per-photo facts into *relatable* facts:

- **Exact/structured queries** ("all photos of Dad") use the existing `tags`/`entities`/
  `tag_references` schema ([../tags/SCHEMA.md](../tags/SCHEMA.md)) — unchanged by this design.
- **Fuzzy/similarity queries** ("find more photos like this one," "show me my countryside") use
  nearest-neighbor search over the embedding column — a photo or a piece of query text gets
  embedded into the same vector space, and pgvector returns the closest matches, ranked by cosine
  distance (this is the "relation-estimate-score" Joakim asked for — it's the similarity score,
  directly sortable).
- **Hybrid**: both axes combine in one query — filter by structured tag/entity, then rank by
  embedding distance, or vice versa. No separate vector database needed; pgvector is a column type
  and an index type inside the same Postgres instance already backing everything else, matching
  [../tags/SCHEMA.md](../tags/SCHEMA.md)'s existing "relational, not graph DB" decision.

See [../GLOSSARY.md](../GLOSSARY.md)'s "Curation and machine perception" section for the plain-language
definitions of embedding/vector database/nearest-neighbor/CLIP, written out in full there.

### 3. The Curator

The orchestration layer that actually talks to the user — proposed name, echoes VISION.md's own
"Metadata, search, and curation" language. Not one neural network; a reasoning/bookkeeping layer:

- Reads the index, decides what's worth surfacing (e.g. a cluster of low blur-score photos).
- Explains *why*, grounded in what the detectors/index actually computed — for V1 this is a fixed
  sentence template filled from real values ("I think you'd like to remove these {n} pictures
  because they were all {reason}"), **not a language model**. Worked example below shows this
  covers more of the target UX than it looks like it would.
- Never applies a suggestion silently — every proposal is shown for review/confirmation, per
  VISION.md Pillar 2's existing "motivated tagging" principle, which this design extends to
  curation suggestions rather than introducing a new rule.
- Incorporates corrections: an excluded photo's embedding becomes a new nearest-neighbor query
  against the index, surfacing related photos for review — again a database query, not generation.

**A real LLM is optional, later, and layered on top — not required for the worked example below.**
If one is ever added (for genuinely free-form conversation beyond what templates cover), it must be
**grounded** — restricted to narrating facts the detectors/index actually produced, never inventing
plausible-sounding claims about a photo's content (the **RAG** — retrieval-augmented generation —
pattern; see GLOSSARY.md). Given POLICY.md's resource-efficiency and closed-by-default/no-cloud-APIs
rules, that LLM would also need to be small and self-hosted — a lower-priority research item, not
started, see [DETECTORS.md](DETECTORS.md)'s local-LLM section.

## Worked example (the one that motivated this design)

> "I think you'd like to remove these 25 pictures because they were all blurry"

`SELECT` photos where the blur detector's score is under threshold, grouped, dropped into a
template with the count and reason filled in. No generation.

> "Yes, but this specific picture is the only one I have of my dog, so I want to keep it"

The Curator removes that one photo from the delete-candidate set. No re-scoring of anything else
needed for that alone.

> "Of course — since I understood that dog was important, I also found these 10 pictures that might
> be the same dog. Please confirm which are Pluto."

The kept photo's embedding becomes a nearest-neighbor query against the whole index; the top-N
closest matches are surfaced as a review batch, tied to the animal-entity flow already designed in
[../tags/UX_FLOWS.md](../tags/UX_FLOWS.md). Still no generation — a similarity query and a template.

> "Please show me all pictures that present my countryside"

The query text is embedded with the same CLIP-style model used on every photo; nearest-neighbor
search against the index returns ranked results, paginated per the user's existing page-size
setting, sortable by the similarity score. This is the one step that genuinely needs a real model
(the embedding model itself) rather than only structured queries — but still no LLM.

## Usage-intent: a score, not a 13th tag category

TAXONOMY.md's 12 categories describe what's **in** a photo. This is a different axis — what to
**do** with it — and it has to be able to change (a photo flips from delete-candidate to keep the
instant a correction lands). A tag is the wrong shape for that: tags are stable until someone edits
them by hand. A recomputed **score** is the right shape — not a user-visible tag, a ranking factor
the Curator reads: detector output (blur/quality) + embedding-cluster membership (near-duplicate
burst?) + entity importance (has the user ever corrected/favorited/shared anything tied to this
photo's entities?) + usage history (`tags.downloaded_at`/`download_count`,
[../tags/SCHEMA.md](../tags/SCHEMA.md), already reserved for exactly this).

This is [../photo-server/DEFERRED.md](../photo-server/DEFERRED.md)'s "usage-based fate prediction"
item, given a real shape — not a new idea, a follow-through on one already flagged as
"needs `audit_log` and album-tag history to accumulate first."

## Should the system wait and learn from deletions before doing anything else?

No. Two reasons: **cold-start** (deletion behavior only teaches the system about photos already
shown to the user — a never-browsed photo teaches nothing by that signal, which is exactly where
detectors are most useful) and **an already-stated dependency** (DEFERRED.md's fate-prediction item
needs `audit_log`/tag history to accumulate first — that history doesn't exist yet, so there's
nothing to learn from on day one regardless). Detectors run immediately and unconditionally
(content-based, available from photo one, shown-not-trusted per the motivated-tagging principle);
explicit corrections layer on top as a second, higher-confidence signal; implicit behavioral signals
(deletes, downloads) get collected from day one via `audit_log` but weighted lower until there's
enough of them to be trustworthy.

## Resource scheduling — the cheapest way to avoid lag

Standard for this class of workload, no exotic mechanism needed:

1. **Never run a detector inline with a user request.** Ingest triggers a background job; browsing/
   search only ever reads already-computed results from the index. A user should never wait on a
   detector to load a page.
2. **A queue, not a new heavy system.** The stack already has Redis (for sessions,
   [../photo-server/TODO.md](../photo-server/TODO.md) Phase 1) — a simple job queue on top of it
   (e.g. RQ) is enough; Celery/RabbitMQ would be disproportionate at this scale. Cap worker
   concurrency at 1, maybe 2 — the i5-650 target is 2 cores/4 threads total
   ([../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)), and the web-serving containers
   (Caddy, auth, Postgres, Redis, photo-viewer) need headroom too.
3. **Load each model once per backlog run, not once per photo.** A persistent worker loads every
   detector at startup, then streams photos through the fixed pipeline — model-load cost paid once,
   not per photo. This is the practical version of "run detectors in series": series across
   *models*, not series-with-a-reload per photo.
4. **Cache aggressively, reprocess only on model-version change.** Process once at ingest time,
   store the result permanently — this is [../policies/POLICY.md](../policies/POLICY.md)'s existing
   "cache aggressively, don't regenerate needlessly" rule, applied to detector output instead of
   thumbnails.
5. **One shared inference runtime, not one per model.** Prefer models available through ONNX Runtime
   (or a similarly lightweight runtime) over ones that each pull in their own heavy framework —
   keeps both RAM and disk footprint down across the whole detector set, not just per-model. The
   existing prototype ([../../prototypes/differentiate_pictures/app/object_identification/obj_id.py](../../prototypes/differentiate_pictures/app/object_identification/obj_id.py))
   runs full YOLOv3 (~236MB) via OpenCV's DNN module — not the lightweight bar this design is
   setting; a replacement pick belongs in [DETECTORS.md](DETECTORS.md)'s object-detection row once
   that area is actually researched.

## Rollout phases this targets

Distinct from — and narrower than — [../VISION.md](../VISION.md)'s own rollout section, which this
doesn't restate. Confirmed with Joakim 2026-08-02:

- **V1 (now)**: a central server — either the existing home box
  ([../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)) or a VPS, undecided, no VPS specs
  documented anywhere in this repo yet so no real comparison exists yet either — flagged in
  [TODO.md](TODO.md), not resolved here. Doesn't block detector/model choice: both candidate hosts
  are far more capable than the eventual Pi-3 floor below, so [DETECTORS.md](DETECTORS.md)'s picks
  work for either; only the deployment target changes.
- **Next**: a PWA doing inference client-side, in each user's own phone or stationary computer's
  browser — not a native app. Needs browser-runnable model formats (ONNX Runtime Web,
  WebGPU/WebNN, or transformers.js-compatible) — a narrower set than a native app could load.
  Real research item once this phase starts; not started, not blocking V1.
  **This is also a refinement of [../VISION.md](../VISION.md) Pillar 2's "inference runs on the
  phone" wording** — that file says "phone," this session's discussion made it concretely a
  browser-based PWA rather than a native mobile app; VISION.md itself isn't edited here since this
  file is the more specific, later-dated source for that detail.
- **End goal (far away)**: Pi-3-class hardware as a router/NAS in every user's own home, running
  this same detection work locally — the target [../photo-server/TODO.md](../photo-server/TODO.md)'s
  "Raised 2026-07-29" stress-test item is queued against.

## Status

Designed 2026-08-02, theory only — no schema migration, no model actually integrated. See
[TODO.md](TODO.md) for the first real test step and open items (VPS specs, model matrix once the
research pass returns).
