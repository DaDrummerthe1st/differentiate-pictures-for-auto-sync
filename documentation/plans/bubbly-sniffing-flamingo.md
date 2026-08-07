# Tag taxonomy: new `documentation/tags/` folder + consolidation

## Context

Tag-related content is currently scattered across `photo-server/DATA_DICTIONARY.md`
(the built `tags`/`kind='album'` mechanism, a reserved `tag_endorsements` table, an
undesigned "Future tag schema" sketch, and a "Tag dimensions" inventory table),
`upload-and-share/OWNERSHIP.md`, `SHARING.md`, `UPLOAD.md`, and `EVENTS.md` (each using
tags as a building block for ownership/sharing/event mechanics), and `VISION.md`
(Pillar 2's tagging vision). None of it defines an actual category model — the goal
this session is to design one and give it one authoritative home under
`documentation/tags/`, per Joakim's framing that tags are **a foundation** the rest of
the idea builds on (not necessarily *the* one foundation) — so this doesn't sit as a
seventh branch-scoped topic folder alongside `photo-server/`/`upload-and-share/`/`gui/`.

**Branching, already done this turn**: confirmed with Joakim, `master` was fast-forwarded
to include all of `upload-and-share` (clean ff, no divergence — verified via
`git merge-base`), and a new `tags` branch was cut from that updated `master`. Local
`master` is now 20 commits ahead of `origin/master`.

**Git-push rule, updated this session**: Joakim confirmed the CLAUDE.md "push is
hand-over-only beyond the current branch" rule is superseded — pushing to `master`
and publishing new branches for coherent, bigger changes is now autonomous, same as
any other push, not a copyable-command hand-over. First implementation step below
updates `CLAUDE.md` itself to say so (traceable decision, not just told to this
session) before pushing `master`.

## Design decisions (confirmed with Joakim this session)

- **Typed categories**, not one generic tag+metadata blob. 8 original + 4 added this
  round based on the "search 'dad', see everything related" use case:
  **origin, people, quality, objects, animals, places, privacy, relationships,
  activity/occasion, story/narrative, temporal/seasonal, co-presence/group.**
  - *Activity/occasion* (skiing, birthday party) is distinct from *origin* (which
    event/upload batch) — one origin can contain many activities.
  - *Story/narrative* is a free-text/linked caption thread spanning multiple
    tags/photos ("the trip where the dog got lost"), not a single-tag attribute.
  - *Temporal/seasonal* (holiday, season, time-of-day) is a human-meaningful
    qualifier distinct from raw EXIF date — "Christmas" or "summer" as a search term
    across years.
  - *Co-presence/group* is a "these people were together" tag, complementary to
    individual person tags.
- **Search is relationship-graph-aware, not just direct-match**: searching "dad"
  must surface (a) photos where he's directly tagged, and (b) photos reachable by
  walking relationship-tag chains from his person-entity (his dog, his motorcycle,
  his home) — even where he isn't directly bounding-boxed in that specific photo.
  `TAXONOMY.md` documents this as an explicit traversal spec, not just a schema note.
- **Unregistered people** are a local-only person record (contact-like, scoped to the
  tagging user), not a bare string — linkable to a real account later. Tagging an
  unregistered person surfaces a CTA: send her an invitation link, or share the
  relevant tag/album with her directly (sharing a tag *is* a category — see below).
  A future "import your contacts to help tag" idea stays in `tags/TODO.md` only, not
  designed now.
- **Relationships are multi-level, chained tags** ("my father's dog" links a
  person-tag and an animal-tag) and **never inherit another tag's bounding box** —
  tagging "my father" next to a dog-tag must not imply he's inside the dog's
  bounding box. Each tag in a chain keeps its own independent, optional bounding box.
- **Tagging UX flow** (captured in a new `UX_FLOWS.md`, not just schema): on-device
  object detection pre-populates subtle, concealable bounding boxes as tap targets.
  Tapping a person box asks "Who is this?", seeded from the detector's own generic
  label ("man"/"woman"), autocompleting against the user's own prior person-entities
  ("da" → "Dad — Pelle Svanslös"). The UI visually distinguishes a tag pointing at a
  registered account from one pointing at a local-only person record. An animal box
  similarly prompts for name, confirmable/changeable type (dog) and breed (labrador),
  plus linking the people in its "herd"/family (relationship tags back to people).
- **Privacy is a tag category**, and **every tag of any category can be shared as an
  album** (not just origin/event tags) — e.g. "my party pictures from Anna's
  birthday" built from an activity or origin tag, shared like any other. Each tag
  still carries a two-value visibility field, `private` (default) or `shareable`,
  independent of the photo's own `photo_owners` ownership terms (a second, narrower
  axis — a `free`-shared photo can still carry a `private` tag keeping it out of a
  shared album view).
  - **Owner-side review UX, before/while sharing a tag as an album**: opening her own
    view of that tag shows every private-flagged photo blurred out, with a banner —
    "every non-blurry picture here will be shared" — so she visually confirms
    exactly what's exposed before it goes out. This is owner-only: a recipient never
    sees a blurred placeholder for a photo she wasn't given access to; excluded
    photos are simply absent from her view.
- **Objects/animals/places reuse people's entity-linking shape**: an owner-scoped
  local record (e.g. "my motorcycle," "my late dog," "home") that repeated tags
  across photos link to, so all photos of the same recurring thing/place become one
  queryable entity — directly serves "search all pictures of my late dog."

## New folder: `documentation/tags/`

Everything tag-related lives physically under this folder — not just referenced from
it. Listed in `documentation/README.md`'s index as cross-cutting, alongside
`policies/` (confirmed with Joakim), not a branch-scoped topic folder.

- **`README.md`** — folder purpose, cross-cutting framing, index of the other files.
- **`TAXONOMY.md`** — all 12 categories, fields, worked examples, the entity-linking
  pattern (people/objects/animals/places), the relationship-chaining rule (no
  bounding-box inheritance), the two-tier visibility model and how it's distinct from
  `photo_owners` ownership, and the relationship-graph search-traversal spec.
- **`SCHEMA.md`** — DB-level shape: `tags` (absorbing the already-built
  `kind='album'` mechanism as the concrete "origin" category), `tag_references`
  (polymorphic pointer: entity, another tag, a pixel region, an email),
  owner-scoped entity tables (people/objects/animals/places), `tag_endorsements`.
  Fully supersedes and absorbs DATA_DICTIONARY.md's "Future tag schema" and "Tag
  dimensions" sections.
- **`UX_FLOWS.md`** — the interaction-level detail: bounding-box tap → autocomplete
  → registered/unregistered visual cue; invite-or-share CTA on tagging an
  unregistered person; animal tagging (name/type/breed/related people); the
  blur-preview sharing-review flow.
- **`TODO.md`** — open, not-decided-now items: user-bio-for-tag-suggestions (future
  idea only), contacts-import idea, nudity auto-detection for the privacy category
  (DPFAS-phase, on-device), reconciling existing `kind='album'`/`kind='content'`
  values with the new category model (implementation-time decision).

## Consolidation edits to existing files

Move content, leave a short stub + cross-reference behind (same pattern
`photo_owners.sharing_terms` already uses pointing at `OWNERSHIP.md`) — never a
pointer-to-a-pointer, and no substantial tag content left duplicated anywhere else:

- **`photo-server/DATA_DICTIONARY.md`**: `tags` table section and `tag_endorsements`
  section → moved to `tags/SCHEMA.md`, one-line stubs left. "Future tag schema" and
  "Tag dimensions" sections removed outright (fully superseded).
- **`upload-and-share/OWNERSHIP.md`**: keep the "tagging is never gated by
  strict/free" paragraph, tightened, with an explicit two-axes note (photo-level
  ownership vs. tag-level visibility) cross-referencing `tags/TAXONOMY.md`.
- **`upload-and-share/SHARING.md`**: "Tag verification/endorsement" schema detail →
  moved to `tags/SCHEMA.md`; short rationale paragraph stays. "Sharing a tag/album"
  section stays (sharing mechanics) but updated to reflect that *any* category is
  shareable as an album, not just `kind='album'`, cross-referencing `tags/TAXONOMY.md`.
- **`upload-and-share/UPLOAD.md`** / **`EVENTS.md`**: one line each noting
  batch-naming and QR-event auto-tags are concretely the "origin" category.
- **`photo-server/DEFERRED.md`**: "Blur and monochrome tags — not designed" line
  corrected — now designed (quality category), still not built.
- **`VISION.md`**: Pillar 2 stays as narrative; add a cross-reference to `tags/` as
  the concrete taxonomy backing manual tagging and future DPFAS content-tags.
- **`photo-server/TODO.md`** Phase 5: note it builds only the origin category; the
  other 11 are future phases per `tags/TODO.md`.
- **`documentation/README.md`**: add the `tags/` row, cross-cutting like `policies/`.
- **`CLAUDE.md`**: update the git-push rule (see below) with a dated decision note.

## Sequencing / commits (all pushes run directly, no hand-over)

1. Update `CLAUDE.md`'s push-authorization language first (dated decision note,
   2026-07-27) — commit, changelog entry, push to `tags` branch.
2. Push local `master` to `origin/master` (plain fast-forward, no force) directly.
3. On the `tags` branch: write the 5 new files, then the consolidation edits, as
   separate coherent commits, each with a `documentation/changelog/` entry and
   `doc_metrics`/`commit_cost` logging. Push each commit to `origin/tags` directly.
4. No code changes, no schema migration — design/documentation only, same stage
   `upload-and-share/` was at before any TDD step was written.

## Verification

Documentation-only change: `tools/documentation_checks` and `tools/redundancy_scan`
after all edits land, confirm every new cross-reference resolves (no
pointer-to-a-pointer), confirm `documentation/README.md`'s index and each touched
file's "Status" line reflect the new state. Report before/after character counts per
touched file in changelog entries and session close, per this project's doc-metrics
rule.
