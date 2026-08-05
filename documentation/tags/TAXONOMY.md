# Tag taxonomy

The category model: what a tag can mean, how categories relate to each other, and
how search walks those relationships. Schema (tables/columns) lives in
[SCHEMA.md](SCHEMA.md); interaction-level detail (tap targets, autocomplete, the
sharing-review screen) lives in [UX_FLOWS.md](UX_FLOWS.md). This file is the
conceptual model both build on.

Designed 2026-07-27. Nothing here is built — see [TODO.md](TODO.md) for what's still
open before implementation starts, and [../photo-server/TODO.md](../photo-server/TODO.md)
Phase 5 for the one category (origin) already partially built under the older
`kind='album'` name.

## The 12 categories

| Category | What it captures | Needs an entity record? | Needs a bounding box? |
| --- | --- | --- | --- |
| **Origin** | Where the photo came from: an event, a wedding, a folder, an upload batch | No | No |
| **People** | Who's in the photo, registered or not | Yes | Optional |
| **Quality** | Blurry, black-and-white, low-colour/pocket-shot | No | No |
| **Objects** | A recurring thing — a motorcycle, a boat, a house | Yes | Optional |
| **Animals** | A recurring pet/animal — species, breed, name | Yes | Optional |
| **Places** | General (a sunny beach, a ski resort) or specific (home, a named car) | Yes | Optional |
| **Privacy** | Restricts exposure — see its own section below | No | No |
| **Relationships** | Links two other tags ("my father", relative to his dog-tag) | No | Optional, own box |
| **Activity/occasion** | What's happening — skiing, a birthday party | No | No |
| **Story/narrative** | A caption thread spanning multiple photos/tags | No | No |
| **Temporal/seasonal** | Holiday, season, time-of-day — human terms, not raw EXIF date | No | No |
| **Co-presence/group** | "These people were together" — a group, not one person | No (links entities) | No |

Origin, quality, activity/occasion, temporal/seasonal are plain tags: a category plus
a value, nothing else attached. People, objects, animals, and places are richer —
see the entity pattern below. Relationships, story/narrative, and co-presence/group
all reuse the same `tag_references` chaining mechanism (see SCHEMA.md) rather than
needing their own table each.

**`category` is a closed enum, deliberately — clarified 2026-08-05.** A tag exists to
communicate one specific thing the system found or was told about a photo — its
category is one of exactly the 12 above, never a free-form value, so a photo can
never accumulate an unbounded pile of ad hoc tag *kinds*, only ever more instances
of these 12 known ones. Two things this rules out, each addressed where it actually
comes up rather than here: a **new detection area doesn't need a new category** —
number-plate detection ([../curation/DETECTORS.md](../curation/DETECTORS.md) area D)
and a custom user-defined category (below) both still resolve to the existing
`privacy` category, only their free-text `tag` value differs; and **not every
detector output becomes a tag at all** — the index layer
([../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)) stores every structured
fact a detector produces for search/matching, but only a curated, confirmed-or-
confident-enough subset ever surfaces as a user-facing tag row. This is also why a
future Curator LLM narration and a tag are two *views* of the same underlying facts,
not two different data models — see ARCHITECTURE.md's Curator section.

## The entity pattern (people, objects, animals, places)

The same shape, reused across all four, because the same need recurs — Joakim's own
example: search every picture of "my late dog" as one thing, not a scattered set of
similarly-worded tags. Each category gets an **owner-scoped entity record** (a
person, a specific motorcycle, a specific dog, "home") that repeated tags across many
photos can point at. Tagging the same dog in ten photos creates ten tags, all
referencing the same one entity — the entity is what search actually matches against.

- **People**: an entity can be a **local-only person record** (contact-like, visible
  only to the tagging user, not the tagged person) or **linked to a real account**
  once that person registers or accepts an invite. Tagging an unregistered person
  surfaces a CTA — see UX_FLOWS.md — to send her an invitation link, or to share the
  relevant tag/album with her directly, since sharing works on any tag (see Privacy
  below), not just this one.
- **Objects/animals/places**: same local-record shape, no account-linking (an object
  doesn't register an account). An animal entity additionally carries species/breed;
  an object entity a type ("motorcycle"); a place entity whether it's general
  (a kind of place) or specific (a named location).

## Relationships — chained, never spatially inherited

A relationship tag references another tag, not a bare entity — "my father's dog"
is a relationship tag whose `tag_references` row points at the dog's animal-tag,
which itself has its own `tag_references` row pointing at the father's person-entity.
**A relationship tag's bounding box, if it has one at all, is independent of what it
references.** Tagging "my father" in relation to a photo of his dog must never be
read as "he is inside the dog's bounding box" — each tag in the chain carries its own
optional box, and the chain link itself carries meaning (which relation — father,
dog, friend's home), not geometry. See SCHEMA.md for exactly how this is represented.

Chains can go more than one hop: a relationship tag can reference another
relationship tag, which is what makes the search behavior below possible.

## Search walks the relationship graph, not just direct matches

Searching "dad" must return more than photos where he's directly tagged. Two result
tiers:

1. **Direct**: photos where a people-tag references dad's person-entity.
2. **Related**: photos reachable by walking one or more `tag_references` hops from
   dad's entity — his dog's photos, his motorcycle's photos, his home's photos —
   even where he isn't personally in frame there. This is what makes "show me
   everything I'd associate with dad while scrolling" actually work, and what makes
   a late pet's whole photo history findable as one search rather than requiring the
   user to remember every tag she ever wrote.

Recommended default: surface direct matches first, related matches as a distinct,
clearly-labelled second group, capped at 2 hops out unless the user asks to expand
further — an unbounded walk over a large tag graph returns too much to be useful as
a default. Not implemented, not finalized — a real search-ranking decision to make
once there's a working graph to test against.

## Privacy — restricts exposure, on any tag

Two independent mechanisms, not one:

- **Ownership** (`photo_owners.sharing_terms`, strict/free — see
  [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)) governs who
  can see the **photo** at all.
- **Tag visibility** governs who can see what a **tag** exposes, and can narrow
  access *below* what ownership would otherwise allow. Every tag, of any category,
  carries a two-value visibility: `private` (default — only the tagging user) or
  `shareable`. A photo shared `free` can still carry a `private` tag that keeps it
  out of a shared album view built from that tag.
- The **privacy category** additionally holds specific semantic values (`nudes`, a children's-photo tag) that force a tag's visibility to `private` — the mechanism behind "a picture of her genitals is automatically kept private." Automating that detection is on-device, DPFAS-phase work — not designed here, see [TODO.md](TODO.md).
- **Custom privacy categories — raised 2026-08-05** (Joakim's example: an inventor whose blueprint photos should default to blurred for everyone except a couple of named exceptions). No new detection model or access-control primitive needed — two existing mechanisms already cover this fully. **Detection**: a custom category is a user-typed free-text description ("an engineering blueprint or technical drawing"), embedded once and compared via the same **zero-shot** similarity check [../curation/DETECTORS.md](../curation/DETECTORS.md) area D's scene-classification pick already uses (CLIP embedding, cosine similarity against a text prompt) — every photo already has this embedding computed for search, so a new custom category costs one text embedding, not a new model or a training pass. A match above threshold surfaces the usual confirm-never-silent prompt, same as any other detector output. **Exceptions**: confirming applies an ordinary `category='privacy'` tag with the user's own label ("Blueprints"), which forces `visibility=private` exactly like the built-in semantic values above — and a `private` tag is still, like any tag, shareable as an album to specifically named people ([../upload-and-share/SHARING.md](../upload-and-share/SHARING.md)) — so "blurred for everyone except two people" is just the owner sharing that one custom-category tag with those two, the same flow as sharing any other tag. No new "allow-list on a private tag" mechanism needed; the existing share-to-specific-people path already is one. Not designed further here: the actual UI for defining a custom category (typing a name + description), and the background job that checks every photo's embedding against every user's custom-category prompts.

## Full provenance/usage disclosure per tag — raised 2026-08-04

Extends the Curator's existing "never applies a suggestion silently, always explains why, grounded in
real computed facts" principle ([../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)) from
*curation suggestions* to *every tag, however it was created*: tapping any tag should show what
produced it (a specific detector + model version, or "typed by you"), its confidence score if
detector-sourced, exactly who can currently see it (derived from tag visibility + the photo's
ownership tier, [../upload-and-share/OWNERSHIP.md](../upload-and-share/OWNERSHIP.md)), and exactly
what it feeds into (the search/embedding index; nothing else, per
[../policies/POLICY.md](../policies/POLICY.md)'s closed-by-default rule — no cloud API, no telemetry,
no third party, ever). The goal, stated plainly by Joakim: a user should be able to verify this for
herself down to the point of satisfying even an unreasonably distrustful reader, not be asked to take
"we don't misuse it" on faith. Not designed further here (no UI, no schema) — a principle to build
toward once tag-detail views exist, related to but distinct from threat #4's still-open third-party
tagging-consent gap ([../security/THREATS.md](../security/THREATS.md)), which is about a *tagged
person's* recourse rather than the *tagging user's* own visibility into her own data.

## Audience circles — a reusable sharing list, not a tag category

Joakim's own question, resolving [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s flagged
"named audience scope doesn't exist yet" gap: **can a group be a tag too, and can a group be one
person?** Second answer: yes, cleanly. First answer, **corrected same session**: not quite — a first
pass modeled a circle as a tag, which broke the enum-boundedness principle above (it would have been
an unenumerated 13th category) and doesn't fit what a tag is *for* here — a circle isn't something the
system found out about a photo, it's a standing sharing list the user authored, unconnected to any
photo at all. **Revised design: a circle is an `entities` row, `entity_type='circle'`**
([SCHEMA.md](SCHEMA.md)) — the same owner-scoped-named-record shape already used for people/objects/
animals/places, just one more instance of it rather than a fifth pattern. Its members live in
`attributes.member_entity_ids`, not `tag_references`, so a circle can never appear in a photo's own
tag list — it structurally can't contribute to per-photo tag clutter, because it was never a
per-photo thing.

- **A circle with one member is just that — no special case anywhere.** Sharing "to a circle" means
  resolving `attributes.member_entity_ids` and fanning out through the existing per-recipient share
  mechanics ([../upload-and-share/SHARING.md](../upload-and-share/SHARING.md)) — one member or ten
  goes through the identical path. Doesn't replace today's direct single-recipient share (typing one
  username/email stays the fast path for a one-off) — a circle is the *reusable, named* version of the
  same mechanism, an addition.
- A member reference resolves exactly like any other people-reference already does: a linked-account
  entity shares directly, a local-only entity falls through to the existing pending-share/email-invite
  flow ([SCHEMA.md](SCHEMA.md)'s `reference_kind='email'`) — no new resolution logic.
- **The earlier naming collision with "Co-presence/group" (this file's category table above) is now
  moot**, not just avoided by word choice: co-presence is a *tag category* (who's depicted together in
  one photo, a content fact); a circle is an *entity type* (a sharing list, never photo content) — two
  different namespaces, so both can safely go on using their own natural words. **Co-presence/group is
  not obsolete and shouldn't be removed** — it answers a genuinely different question a circle can't
  ("who's in this specific photo together" vs. "who do I usually share things with"), and nothing
  about this session's design touches it.

Not designed further here: the actual UI for creating/editing a circle, and whether
[curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s privacy-preference aggregate's "public" tier
(everyone, not a specific named circle) is itself just a special built-in circle or a separate concept
— flagged, not resolved.

## Every tag is a shareable album — with a visual pre-share review

Any tag, of any category, can be shared as an album, not just origin/event tags —
"my party pictures from Anna's birthday" can be built from an activity tag exactly
like an origin tag can. Sharing a tag shares live, matching the existing album model
in [../upload-and-share/SHARING.md](../upload-and-share/SHARING.md).

Before or while sharing, the tag owner's own view of that tag shows every
`private`-flagged photo inside it **blurred**, with a banner: "every non-blurry
picture here will be shared." This is a visual confirmation step, owner-side only —
a recipient never sees a blurred placeholder for a photo she was never given access
to; excluded photos are simply absent from her view. Full interaction detail:
[UX_FLOWS.md](UX_FLOWS.md).

## Status

Designed 2026-07-27, taxonomy only — no schema migration, no endpoints. Supersedes
[../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md)'s old
"Future tag schema" and "Tag dimensions" sections outright. **2026-08-04**:
provenance/usage-disclosure principle added. **2026-08-05**: category-enum-boundedness
clarified, custom privacy categories added, audience circles designed (as an `entities`
type, not a 13th category — see that section for the correction).
