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

**Search/storage at distributed scale is Pillar 1's problem, not this file's, confirmed 2026-08-03**:
this design's pgvector index assumes one Postgres instance (today's single server/VPS, per
[../VISION.md](../VISION.md)'s "single VPS is the sole source of truth for all current work"
constraint). Once Pillar 1's DFS spreads photo bytes (and their embeddings) across many independent
nodes, nearest-neighbor search across a sharded, distributed vector index is a genuinely harder
problem than anything designed here — correctly out of scope for curation/, tracked instead as
[../distributed-sync/TODO.md](../distributed-sync/TODO.md)'s existing open "where does metadata live
once bytes are distributed" question, which embeddings are just another instance of.

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
- **Undo is mandatory, not a nice-to-have, and is itself a signal** (raised 2026-08-03): any
  suggestion the Curator acts on needs a full undo path, because a mis-tap on a real device is
  certain to happen and a wrongly-applied high-confidence correction is worse than a wrongly-applied
  low-confidence one (it propagates further via the nearest-neighbor re-search above). Beyond safety,
  undo is itself a usage-intent input, distinct from an explicit correction: it can mean either "I
  made a mistake" (noise, should barely move any score) or "I'm not actually sure" (a real, if weak,
  low-confidence signal) — which of the two it is isn't automatically knowable from the undo event
  alone. Not designed further here; flagged as a real open UX question, not resolved.

**Is the Curator a real thing "from the start," or an MVC View?** Neither, precisely — nothing here
is built yet (see Status below: theory only). And when it is built, it isn't a View: the View is
the actual GUI the user sees; the Curator is closer to a Controller/service layer that reads the
Model (the index) and decides what the View should show and why — the View then renders whatever
the Curator hands it. Worth naming plainly since "View" would be a real misdescription once code
exists.

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

**Multiple ways a user signals importance, and a re-weighting of which usage signals actually matter
(raised 2026-08-03)**: at least two distinct input types feed this score, not one — **deliberate**
(e.g. a user tags a photo densely enough that it's implicitly excluded from any delete-candidate
cluster — "if I've tagged this photo this much, it matters") and **incidental/behind-the-scenes**
(e.g. a user consistently keeps only one photo out of every near-duplicate burst at a given
timestamp — area E's burst-clustering feeds this directly: which *one* of the cluster survives a
user's own past behavior is itself a training signal for which one to suggest keeping next time).
Separately, a correction to this file's own [DEFERRED.md](../photo-server/DEFERRED.md)-inherited
field list: **`downloaded_at`/`download_count` are comparatively low-value signals** — a download is
a one-off, arguably obsolete once in-app viewing/sharing exists. **Sharing a photo, adding it to an
album/tag ("folderization"), being viewed repeatedly, and appearing as a hit against a past search
are all stronger signals of importance than a download**, and should weight higher. A photo that
keeps surfacing as a *search result* the user then acts on (opens, shares, tags) should score higher
still — search-hit-then-engaged is a compound signal, not just a raw hit count. None of this is
implemented; it corrects the signal list above, not `../tags/SCHEMA.md`'s already-reserved columns
(those stay as one input among several, just a weaker one than originally implied).

**Privacy-decision preference aggregate — raised 2026-08-05**: Joakim's own proposed shape,
`"email": "blurred-public:93%-contacts:45%-closeFriends:3%"` — a per-(PII-category × audience-scope)
rolling percentage of how often the user has chosen to blur that category of detected content when
sharing to that scope, computed from the OCR-privacy-tag confirm/blur history
([../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s privacy section). Same shape as the usage-intent score
above, not a new kind of thing: a recomputed signal derived from corrections, never a stable tag,
used only to **pre-fill** the next confirm-or-blur prompt with a suggested default ("you've blurred
emails shared publicly 93% of the time — blur this one too?") — never an auto-decision, same
motivated-tagging principle as everywhere else in this design. **Real dependency, partly resolved 2026-08-05**:
this assumes named audience scopes ("public," "contacts," "close friends") as a first-class concept,
which didn't exist as of the previous session. [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s new
"Audience circles" section now designs exactly that primitive — a circle is a tag (reusing
`tag_references`, same mechanism as everything else in this taxonomy), with a one-member circle as
the unremarkable base case, not a special one. Still open: whether a "public" tier is a real built-in
circle or a separate concept, and the schema note that a circle tag needs `tags.photo_id` relaxed to
nullable — both flagged in that section, not resolved here either.

**Every automated suggestion needs a visible confidence estimate**, not just a yes/no proposal — the
"relation-estimate-score" concept from the countryside-search example generalizes to every Curator
suggestion, not only similarity search: a delete-candidate cluster, a "possibly the same dog" batch,
and a tag suggestion should all surface how confident the underlying detector/index evidence is, so
the user can calibrate trust per-suggestion rather than treat every proposal as equally certain.

**Two different embedding spaces, not one (raised 2026-08-03)**: the CLIP-style whole-photo embedding
above is tuned for *scene/vibe* similarity — background and composition are part of what it matches
on, which is exactly right for "find more countryside photos" but weaker for "find this specific dog
regardless of background," since a whole-photo vector for a dog on a beach and the same dog in a
kitchen may sit far apart. **Identity matching (a specific person, pet, or object regardless of
surroundings) needs a second, separate embedding computed from a *cropped* detector region**, the
same principle [DETECTORS.md](DETECTORS.md) area B's face-recognition pick already uses (detect the
face, crop it, embed *that* crop) — animal/object identity matching (area C) would need the same
crop-then-embed treatment, not a reuse of the whole-photo CLIP vector, once that area is researched.

**This design also lays real groundwork for training a custom model later, not just for using
off-the-shelf ones (raised 2026-08-03)**: every explicit correction the Curator collects (kept/
excluded, confirmed/rejected identity matches) is a labeled example — exactly what a custom model
would need to train on. Training one from scratch today would be a disproportionate undertaking (see
[DETECTORS.md](DETECTORS.md)'s series-vs-shared-backbone note on why no off-the-shelf multi-task net
fits this project's exact mix), but the correction/feedback loop this architecture already designs
is what would make a future custom model *feasible* rather than starting from zero — worth keeping in
mind as a reason to get the correction-logging shape right now, even though no training work is
planned yet.

**Per-household few-shot identity classifier — resolves pet identity matching's "no confident pick"
gap (raised 2026-08-03)**: [DETECTORS.md](DETECTORS.md) area C found no pretrained animal
re-identification model that's both permissively licensed and actually good at telling individual
animals apart (raw foundational embeddings like CLIP are documented in the literature as poorly
adapted to fine-grained instance-level identity without fine-tuning). Rather than waiting for one,
**each household trains its own tiny classifier**, using only its own labels, on top of the
embedding it already computes for free — the CLIP crop-embedding for animals, the MobileFaceNet
embedding for people (area B). No new model to source or license: the cheap baseline from the very
first label onward is nearest-neighbor against confirmed reference embeddings per entity (the same
mechanism already planned for face-recognition's `entities` matching); once enough labeled examples
accumulate per identity, a trained linear-probe classifier (e.g. logistic regression) on the same
frozen embeddings is a natural, still-CPU-cheap upgrade for cleaner boundaries between visually
similar individuals — seconds of CPU time to fit, not a training job. **Confirmed with Joakim
2026-08-03: this generalizes to both people and animals**, not just pets — for people it's additive
to the existing generic-embedding design (which already works reasonably without per-household
training), for animals it's the actual fix for the "no confident pick" gap.

*Bootstrap/cold-start mechanism*: a **gamified labeling session** — short, bounded ("five minutes to
spare"), the user fed one already-detected-but-unidentified crop at a time from photos or sampled
video-clip frames, asked to confirm/correct/name it — is the active mechanism that solves this
file's own cold-start problem (below) rather than waiting passively for browsing/deletion behavior
to accumulate signal. Suggestions are expected to be poor at first and improve as labels accumulate,
same arc as any few-shot classifier. UX-flow-level detail: [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s
new "Gamified identity-labeling session" section.

*Cross-household reuse ("user1 has photos of user2's dog/spouse") is two separate problems, not one*,
raised and partly resolved 2026-08-03:
- **Consent/trust** — sharing another household's trained classifier or reference embeddings across
  a household boundary touches someone's biometric-adjacent data (see [../GLOSSARY.md](../GLOSSARY.md)'s
  "biometric data" flag on the age/gender item), so it needs the same conscious opt-in treatment, not
  a default. **Resolved as policy 2026-08-03**: each household/training decides, per entity, what (if
  anything) to share and with whom — an explicit opt-in.
- **Mechanism** — actually transferring/merging a classifier, reference embeddings, or labels across
  two independent servers is a distributed-sync problem this file has already punted once (see the
  pgvector-at-scale note above): genuinely blocked on whatever cross-server sync protocol
  [../distributed-sync/TODO.md](../distributed-sync/TODO.md)'s V2/V3 work eventually builds, not
  something to design here. The consent policy above stands regardless of when the mechanism exists.

**How cross-household linking could actually work — real answer, raised 2026-08-05** (Joakim's
example: household A tags a real person "Jocke," household B independently tags the same real person
"Joakim," both want the two connected). Two structurally different cases, needing two different
mechanisms — conflating them would be a mistake:

- **The subject has, or can get, her own account — the solvable case, no new mechanism needed.**
  [../tags/SCHEMA.md](../tags/SCHEMA.md)'s existing `linked_account_user_id` is exactly the join point:
  household A's "Jocke" entity and household B's "Joakim" entity can each independently link to *the
  same* real account, via the *already-designed* email-bound invite flow
  ([../security/THREATS.md](../security/THREATS.md) #11), run twice — once per household. **This
  sidesteps the whole cross-network embedding-comparison problem entirely**: neither household's
  private face index, reference embeddings, or raw photos ever have to leave its own server, because
  the *linking* is done by the real person herself confirming "yes, that's me" through an authenticated
  invite, not by any automated cross-household face comparison. This is the resolved, buildable answer
  for people, and requires nothing beyond what's already designed. One real limit, not solved by this:
  [../distributed-sync/METADATA.md](../distributed-sync/METADATA.md)'s "raw tag data stays
  owner-controlled" rule means this linking doesn't, by itself, let either household see the other's
  private tags of her — it only gives the subject herself a common identity to potentially aggregate
  her own data across, which is a separate, not-yet-designed feature.
- **The subject has no account and never will (an animal, or a person who stays local-only) — the
  genuinely hard case, still open.** There's no authenticated party who can confirm "yes, same
  individual" the way a registered person can for herself, so any connection would have to come from
  directly comparing the two households' private data — exactly what's already ruled out (EDPB Opinion
  11/2024, [../security/TODO.md](../security/TODO.md) item 6: never let a decrypted/usable embedding
  leave its subject's own device or reach a shared index). **Real cryptography exists for this
  class of problem** — Private Set Intersection (PSI) / Privacy-Preserving Record Linkage (PPRL,
  see [../GLOSSARY.md](../GLOSSARY.md)) lets two parties learn only which records match, without
  revealing anything about non-matching ones — but researched 2026-08-05: classic PSI targets
  discrete/exact-match fields (e.g. hashed emails), not fuzzy nearest-neighbor similarity over
  continuous face/animal embeddings, which is what identity matching actually needs — and, same
  caveat already logged for homomorphic encryption/secure multiparty computation
  ([../security/TODO.md](../security/TODO.md) item 6), no source found proves it runs on this
  project's Pi-class target hardware. **Left genuinely open**: for an animal or a local-only person,
  connecting two households' independent labels isn't solvable today without either violating the
  no-shared-embeddings rule or waiting on research that isn't deployment-ready — consistent with, not
  a new gap beyond, this section's existing "mechanism blocked on distributed-sync V2/V3" framing.
  Who would even hold consent authority for a dog (neither tagging household unilaterally, presumably
  whichever household actually owns/owned the animal) is itself unresolved, flagged not answered.

**Mislabeling / false-identification risk on people — flagged, not resolved (raised 2026-08-03)**:
because every name-tag is a private, human-asserted claim rather than a verified fact (per this
file's own "never applies a suggestion silently" principle, the AI itself never asserts an identity —
only a human does, by confirming or typing one), nothing currently stops a user from mislabeling a
face — by mistake, or in bad faith — with a real named person's identity. The concrete risk raised:
if such a private label is ever exported, shared, or screenshotted, it could be presented as though
it were a verified identification (e.g. wrongly placing a real named person at a real event — a bank
robbery, a war zone — she was never actually at). This is a liability/privacy question distinct from
detector accuracy, and distinct from — but same-shaped as — the existing age/gender and OCR-in-frame
privacy flags in [DETECTORS.md](DETECTORS.md). **Not designed here**: left as an open item for a
future privacy-focused session, same treatment as those other flags, rather than resolved today.

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

**Considered and rejected: pay-as-you-go cloud GPU for the detector stage** (raised 2026-08-03,
resolved same day). This would mean photo bytes leaving the server for third-party inference — a
direct conflict with [../policies/POLICY.md](../policies/POLICY.md)'s closed-by-default rule ("no
photo or user data ever leaves the server the user controls. No cloud APIs."), not just a
resource-efficiency tradeoff. **Confirmed with Joakim: the rule stands** — detectors stay self-hosted,
CPU-only, regardless of the convenience/speed a cloud GPU service would offer.

## Upload flow should reflect this design (flagged, not designed here)

Raised 2026-08-03: this session's category model (what a detector/the Curator can infer
automatically) should inform what the upload flow prompts a user for at upload time — e.g. album/
folder/occasion, mirroring the origin category ([../tags/TAXONOMY.md](../tags/TAXONOMY.md)). Belongs
in [../upload-and-share/UPLOAD.md](../upload-and-share/UPLOAD.md) (already designed, not yet built —
see [../photo-server/DEFERRED.md](../photo-server/DEFERRED.md)'s "Upload function" entry), not here —
flagged as a cross-reference for whichever session actually specs the upload UI, not solved in this
design pass.

## Rollout phases this targets

Distinct from — and narrower than — [../VISION.md](../VISION.md)'s own rollout section, which this
doesn't restate. Confirmed with Joakim 2026-08-02:

- **V1 (now)**: a central server — either the existing home box
  ([../photo-server/HARDWARE.md](../photo-server/HARDWARE.md)) or a VPS, still undecided, but both are
  now specced ([TODO.md](TODO.md)'s VPS section: Contabo Cloud VPS 10, 4 vCPU AMD EPYC, 7.8GB RAM,
  hosted at Lauterbourg, France — EU, verified). Doesn't block detector/model choice: both candidate
  hosts are far more capable than the eventual Pi-3 floor below, so [DETECTORS.md](DETECTORS.md)'s
  picks work for either; only the deployment target changes.
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
