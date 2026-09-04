# Usage-intent scoring and identity matching

Split out of [ARCHITECTURE.md](ARCHITECTURE.md) 2026-08-05 (that file had grown to ~30K characters
covering several distinct sub-topics; this is the one that grew the most after the initial
2026-08-02 design) — read ARCHITECTURE.md first for the three-layer model and the Curator this
content builds on. Everything below was designed 2026-08-03 through 2026-08-05; dates are kept
inline per entry rather than restated here.

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
motivated-tagging principle as everywhere else in this design. **Real dependency, resolved 2026-08-05**:
this assumes named audience scopes ("public," "contacts," "close friends") as a first-class concept,
which didn't exist as of the previous session. [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s new
"Audience circles" section now designs exactly that primitive — a circle is an `entities` row
(`entity_type='circle'`, [../tags/SCHEMA.md](../tags/SCHEMA.md)), not a tag, with a one-member circle
as the unremarkable base case, not a special one. Still open: whether a "public" tier is a real
built-in circle or a separate concept — flagged in that section, not resolved here.

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
  two independent servers is a distributed-sync problem this file has already punted once (see
  [ARCHITECTURE.md](ARCHITECTURE.md)'s pgvector-at-scale note): genuinely blocked on whatever
  cross-server sync protocol [../distributed-sync/TODO.md](../distributed-sync/TODO.md)'s V2/V3 work
  eventually builds, not something to design here. The consent policy above stands regardless of when
  the mechanism exists.

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
because every name-tag is a private, human-asserted claim rather than a verified fact (per
[ARCHITECTURE.md](ARCHITECTURE.md)'s own "never applies a suggestion silently" principle, the AI
itself never asserts an identity — only a human does, by confirming or typing one), nothing currently
stops a user from mislabeling a face — by mistake, or in bad faith — with a real named person's
identity. The concrete risk raised: if such a private label is ever exported, shared, or
screenshotted, it could be presented as though it were a verified identification (e.g. wrongly
placing a real named person at a real event — a bank robbery, a war zone — she was never actually
at). This is a liability/privacy question distinct from detector accuracy, and distinct from — but
same-shaped as — the existing age/gender and OCR-in-frame privacy flags in [DETECTORS.md](DETECTORS.md).
**Not designed here**: left as an open item for a future privacy-focused session, same treatment as
those other flags, rather than resolved today.

## "Two Per Holmgrens" — disambiguation is required at labeling time, not just on collision

Resolved 2026-09-05, Joakim's own framing: a bare display name doesn't distinguish two different
real people who happen to share one (his example: two people both named "Per Holmgren"). Considered
against two lighter alternatives — do nothing extra by default and only prompt for disambiguation
once a name/embedding collision is actually detected, or make a disambiguation field optional and
never enforce it — **Joakim chose the strictest of the three**: every `person` entity gets a
disambiguation note and a reference photo **required at creation**, before either name-collision or
embedding-collision detection ever runs, not conditioned on one.

**Why required-always beats collision-triggered**: a collision check ([../tags/TODO.md](../tags/TODO.md)'s
entity-merge-dedup section design the embedding-similarity trigger for the *inverse* problem — one
person, two entities) can only fire once a second entity already exists to collide against. The first
"Per Holmgren" entity, created alone, would otherwise carry nothing but a name — exactly the state
that makes the *second* one ambiguous the moment it's typed. Requiring the note/photo from entity
number one closes that gap instead of leaving it open until a collision happens to occur.

**Shape**: [../tags/SCHEMA.md](../tags/SCHEMA.md)'s `entities.attributes` JSONB, person type, gains
`disambiguation_note` (free text — "cousin, met at Anna's wedding," "colleague at Ericsson") and
`reference_photo_id` (points at one of the photos this entity is already tagged in — not a new
upload, since a person entity is never created except by tagging her in at least one photo first).
Both required at the same UI step that creates the entity, in whichever flow that is — the gamified
cold-start session ([../tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s "Gamified identity-labeling session")
and any ad hoc "tag this face" moment outside that session both create entities the same way, so both
need the same required fields, not two divergent creation paths.

**Where this surfaces**: autocomplete/search results showing two entities named "Per Holmgren" render
the disambiguation note (and a thumbnail from `reference_photo_id`) alongside the name, so choosing
between them is a real decision rather than a guess — same principle as [ARCHITECTURE.md](ARCHITECTURE.md)'s
"never applies a suggestion silently," extended to disambiguation rather than to confirmation.

**Not designed here**: the actual autocomplete/search UI treatment (belongs in
[../tags/UX_FLOWS.md](../tags/UX_FLOWS.md)), and whether an existing person entity created before this
rule (none exist today — nothing is built yet, see Status) would ever need backfilling — moot until
real data exists.

## Native app avoided as long as possible — resolved for redundancy-contribution, stated as a general stance

Resolved 2026-09-05, following on from [ARCHITECTURE.md](ARCHITECTURE.md)'s PWA-vs-native capability
check (2026-09-04): that check found manual/one-time photo picking for DFS redundancy contribution
works fine from a PWA, and only *automatic/continuous background* contribution would force a native
app, and only on iOS. Asked directly whether Joakim wants that automatic behavior badly enough to
accept a native app for it — **he does not**: manual/in-app picking is accepted, and the reasoning
goes beyond this one feature. Joakim's own framing: the whole point of self-hosting on each user's own
NAS (or network of NASes) is that *he* controls the code running there; publishing through Google
Play or the Apple App Store hands each platform owner standing latitude to modify or re-sign the app
binary on its way to users, which conflicts with that control model at a deeper level than any single
feature's UX. **So "avoid a native app for as long as possible" is a standing architectural stance,
not just this feature's answer** — the redundancy-contribution question is the first concrete case it
resolved, not the only one it applies to. A native app stays a last resort, considered only if some
future capability turns out to have no PWA-reachable path at all, not reached for on convenience
grounds.

## Contacts-import desktop fallback — CardDAV confirmed real, build deferred to a guided session

Raised 2026-09-04/05 alongside the desktop Contact Picker gap ([../security/THREATS.md](../security/THREATS.md)
row 17, [../tags/TODO.md](../tags/TODO.md)'s Contacts import item): Joakim asked whether something like
Thunderbird's contact syncing exists for this purpose. **Researched 2026-09-05 — confirmed real**:
CardDAV (RFC 6352) is an open standard for exactly this, supported by Google Contacts, iCloud, and
Thunderbird's native client (see [../GLOSSARY.md](../GLOSSARY.md)'s new CardDAV entry for the
mechanism). Chosen as the target design for the desktop fallback, with an explicit requirement Joakim
added: it must be able to **re-sync when a searched name isn't found**, not just a frozen one-time
export — a standing (if user-triggered) connection, not a single snapshot.

**Real tradeoff this reopens, not fully resolved**: CardDAV authenticates once (Google OAuth or an
iCloud app-specific password) and then exposes the *whole* address book, a different exposure shape
than the mobile Contact Picker API's one-contact-at-a-time disclosure that row 17 chose specifically
to minimize bulk list access. CardDAV doesn't touch row 17's other axis (person↔photo linkage never
reaching Google — CardDAV is read-only, contacts-in only) but does reintroduce standing bulk access
on the list-exposure axis, on desktop only. Not yet decided: whether that tradeoff is accepted as the
cost of desktop parity, or whether the desktop fallback should stay deliberately narrower than mobile.

**Build deferred, not designed further today**: an actual CardDAV integration needs Joakim to do
things only he can do — register an OAuth client (Google) or generate an app-specific password
(iCloud) against his own real account — so building and demoing it is deferred to a separate,
guided session where those account-side steps happen interactively, rather than attempted blind in
this design pass. Flagged in [../tags/TODO.md](../tags/TODO.md) so it isn't lost.

## Status

Split from [ARCHITECTURE.md](ARCHITECTURE.md) 2026-08-05 — content dates unchanged (2026-08-03
through 2026-08-05), see each entry inline. **2026-09-05**: three design questions resolved with
Joakim — person-entity disambiguation required at labeling time, native app avoided as a standing
architectural stance (not just for redundancy-contribution), and CardDAV confirmed as the desktop
contacts-fallback target design (build deferred to a guided session). Nothing here is built; no
schema migration, no model integrated.
