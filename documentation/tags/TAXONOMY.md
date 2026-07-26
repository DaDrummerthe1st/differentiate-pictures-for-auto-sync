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
- The **privacy category** additionally holds specific semantic values (`nudes`, a
  children's-photo tag) that force a tag's visibility to `private` — the mechanism
  behind "a picture of her genitals is automatically kept private." Automating that
  detection is on-device, DPFAS-phase work — not designed here, see
  [TODO.md](TODO.md).

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
"Future tag schema" and "Tag dimensions" sections outright.
