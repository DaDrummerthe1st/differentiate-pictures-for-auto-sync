# Gamified curation sessions — spec

Split out as its own file 2026-08-05, at Joakim's request: [tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s
"Gamified identity-labeling session" (2026-08-03) sketched one narrow case — pet/person identity
labeling — and explicitly left the actual game mechanic ("streaks, a completion reward, some other
engagement device") **not decided**. This file generalizes that mechanic across every kind of
Curator finding a user can confirm/correct/decline, and designs the parts left open: what earns
credit, what credit is *for*, and how a session's output feeds back into model training — both the
already-designed per-household classifier and a new, more carefully-scoped system-wide question.
Vision-level design, same bar as every other file in this folder — not build-ready, no schema
migration, no endpoints.

## A terminology correction, worth stating plainly

"Training the user's own embeddings" isn't quite the right phrase, and it's worth being precise here
since the rest of this file depends on the distinction. **The embedding models themselves are frozen
— never retrained, by a household or by anyone.** CLIP (crop-embed for animals/objects) and
MobileFaceNet (faces) run exactly as pretrained, unchanged, forever — that's what makes them cheap
enough to run on this project's target hardware in the first place. What a household actually trains
is a **small classifier that sits on top of those frozen embeddings** — starting from a
nearest-neighbor lookup against confirmed reference embeddings (no training at all, the day-one
baseline), optionally upgrading to a fitted linear-probe/logistic-regression classifier once enough
labels accumulate (seconds of CPU time, [IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)'s existing
design — not duplicated here). So: the *embeddings* are computed, never trained; the *classifier* is
what training actually means in this project's pipeline.

## What counts as a round — generalized beyond identity

[UX_FLOWS.md](../tags/UX_FLOWS.md)'s existing session structure (a bounded entry point, one item per
round, cold-start blank prompts warming into confirm/correct suggestions, never an auto-accept) is
right and stays as designed — this section only widens *what* a round can be about, since identity
labeling is one instance of a much more general shape: **every detector/Curator finding this project
has designed needing human confirm-or-correct is a valid round type**, not just "who/what is this":

| Round type | What it asks | Source |
| --- | --- | --- |
| Person/animal identity | "Who/what is this?" / confirm-or-correct a classifier guess | [IDENTITY_MATCHING.md](IDENTITY_MATCHING.md), existing |
| Group/co-presence | "Are these two people together in this photo?" | [DETECTORS.md](DETECTORS.md) area B, 2026-08-05 |
| Age/gender guess | Confirm/correct a rough demographic estimate | DETECTORS.md area B, 2026-08-05 |
| Best-shot / near-duplicate pick | "Which of these N shots is the keeper?" | DETECTORS.md area A, still a design-only feature, see its own bias-risk flag below |
| Pose/action guess | Confirm/correct "what is this person doing" | DETECTORS.md area J, 2026-08-05 |
| Relationship confirm | "Is this Dad's dog?" — confirm a suggested `tag_references` chain | [../tags/TAXONOMY.md](../tags/TAXONOMY.md) |

**Deliberately excluded from this list: privacy-category confirm/blur decisions** (OCR-detected text,
number plates, nudity flags). Gamifying a decision with real consequences if rushed — "is this
information sensitive enough to blur" — risks encouraging fast, low-attention taps on exactly the
judgment call this project's own confirm-or-blur flow exists to slow down and take seriously
([../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s privacy section, DETECTORS.md area D's data-minimization
note). These stay their own dedicated, un-gamified flow — no points, no session inclusion. Same
reasoning as this project's existing mislabeling-risk flag
([IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)): a reward mechanic must never create an incentive to
label faster/carelessly on anything where being wrong has real cost to someone.

## The reward mechanic — decided, where UX_FLOWS.md left it open

**No streaks, no countdown timers, no loss-aversion mechanics** ("don't break your streak!") — these
are the standard dark-pattern engagement tools, and they cut directly against VISION.md Pillar 2's
own standing design principle: *motivated* tagging, real engagement with one's own photos, not
tagging-as-chore-for-points. A reward mechanic that makes someone tag faster/more anxiously to avoid
losing something would be optimizing for the wrong outcome — this project's whole point is to get
better information out of a relaxed, genuinely-attentive round, not more rounds.

**What earns credit, and how much — tied to actual training value, not to being "right"**: there's no
ground truth to check a label against at labeling time, so correctness can't be the basis for
reward — rewarding "correct" answers over "honest, uncertain" ones would itself create a perverse
incentive to guess. Instead, credit scales with how much new information a round actually
contributes to the system, which this project can already estimate from the same logic
[IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)'s active-learning framing already uses:

- **Naming a brand-new identity** (the first labeled example the classifier has ever seen for this
  person/animal) — highest credit. This is the hardest-to-get, most valuable label: it's what turns a
  cold-start blank prompt into a workable few-shot anchor.
- **Correcting a wrong classifier guess** — second-highest. A correction is a stronger training
  signal than a confirmation (it's the actual boundary-case information a linear-probe classifier
  needs to improve), same reasoning already established for usage-intent scoring's
  deliberate-vs-incidental signal split.
- **Confirming a correct guess** — base credit. Still useful (reinforces confidence, feeds the
  nearest-neighbor baseline), but the lowest-information-content case of the three.
- **"I don't know" / skip** — small but non-zero credit, explicitly never zero. This is the
  load-bearing anti-perverse-incentive design choice: if skipping earns *nothing* while guessing
  earns *something*, a user is incentivized to guess rather than skip, which pollutes the classifier
  with wrong labels exactly when it's most fragile (few-shot, cold-start). A skip is a legitimate,
  rewarded outcome, not a failure to reward.

**What credit is *for***: this project has no monetization/paywall in its current design phase
(VISION.md's V1/V2 scope), so credit isn't currency for anything — it's **visible, private progress**,
shown the way a photo library's own stats already are (Joakim's account, not a public leaderboard
service): a running tally ("You've helped identify 230 photos"), optionally a same-household
leaderboard if more than one person tags (low-stakes, opt-in — a household choosing to make it
visible to each other, not a default). No unlockable features gated behind it, no artificial scarcity.
If a future commercial phase ever wants to gate something behind engagement, that's a distinct
decision for whoever designs that phase, not assumed here.

## Session and event logging — reuses `audit_log`, not a new table

Every round's outcome (which finding, what the user did, and the credit awarded) is exactly the kind
of fact [`audit_log`](../photo-server/DATA_DICTIONARY.md) already exists to hold — same
`(user_id, action, details JSONB, created_at)` shape, a new `action` value per round type
(`curation_round_completed`) rather than a dedicated points table. This isn't just schema economy:
the same event row that computes a user's running tally is also the labeled-correction record
[IDENTITY_MATCHING.md](IDENTITY_MATCHING.md) already says a future custom model would train on —
one log serves both the game and the training pipeline, no risk of the two drifting out of sync with
each other. Points themselves are a computed sum over this log at read time (same "recomputed score,
not a stable stored counter" pattern as the usage-intent score,
[IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)), not a separately maintained, driftable counter.

## Training fold-in, part 1: per-household — already designed, restated briefly

[IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)'s per-household few-shot classifier is the mechanism
every identity-type round above actually feeds: nearest-neighbor from the first label, a fitted
linear-probe classifier once enough labels accumulate, entirely local to that household's server, no
raw embedding ever leaving it. Not redesigned here — this file's job was the session/reward layer on
top, which that file explicitly left to a future session (its own "Bootstrap/cold-start mechanism"
note points here).

## Training fold-in, part 2: system-wide — a real tension, resolved narrowly, one part left open

Joakim's question ("or a system wide training") runs into a genuine, already-partly-decided tension
in this project's own docs, worth naming rather than glossing over:

- [VISION.md](../VISION.md) Pillar 2 states an aspiration that curation suggestions get "learned
  globally across the network," and [../distributed-sync/METADATA.md](../distributed-sync/METADATA.md)
  once floated "an anonymous index of embeddings and engagement counts" as the shareable layer.
- But [IDENTITY_MATCHING.md](IDENTITY_MATCHING.md)'s own resolved cross-household-linking research
  (2026-08-05) is explicit that **no version of this design should ever publish raw, usable
  embeddings anywhere** (EDPB Opinion 11/2024's reconstruction-attack risk) — and
  METADATA.md's own later, more carefully-researched section ("Private, per-user face matching,"
  2026-07-29) already corrected course on this exact point: every user's face/identity index stays
  private, un-published, "at any scale," full stop.

**Resolution for identity/embedding data: not open, already settled by the more carefully-researched
of the two positions above — identity-linked embeddings, reference vectors, and per-household
classifiers never leave the household's own server, contribute to no shared index, and are never
part of any "system-wide" training, gamified or not.** This file doesn't reopen that.

**What a legitimate system-wide training channel could still look like — flagged, not designed to
build-ready**: the *general-purpose, off-the-shelf* detectors (RapidOCR's pattern-match accuracy,
the age/gender model's accuracy, the pose/action heuristic's accuracy, a future best-shot model) are
a different kind of thing entirely from a household's private identity classifier — a correction like
"this OCR text-region confidence was wrong" or "this pose guess was wrong for this crop" carries no
name, no entity, no identity link at all, only a generic (input, wrong-guess, corrected-guess) triple.
**An opt-in mechanism to contribute exactly that — anonymized, non-identity-linked correction
examples — back to whoever maintains the shared model files, for a future offline retraining/
fine-tuning pass, not real-time cross-household model merging** — is consistent with everything
already decided above and would be the buildable interpretation of "system-wide training." Real
federated learning (households collaboratively training a shared model without any raw data ever
leaving any device) is a genuinely different, much heavier mechanism — a real technique, not
researched here, and not assumed as the answer. **Left as an open design call for Joakim**: whether
"system-wide training" means the lightweight opt-in-correction-export version sketched here, the
heavier federated-learning version, or isn't wanted at all yet — not resolved by this file.

## Status

Opened 2026-08-05, split out of [tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s narrower
identity-labeling-only sketch per Joakim's explicit request to generalize the mechanic, decide the
reward design UX_FLOWS.md had left open, and fold in the model-training question (both per-household
and system-wide). Nothing here is built — no schema migration (the `audit_log` reuse above is a
design choice, not a migration), no endpoints. See UX_FLOWS.md for the interaction-level round detail
this file doesn't repeat, and IDENTITY_MATCHING.md for the classifier mechanics this file's rounds
feed into.
