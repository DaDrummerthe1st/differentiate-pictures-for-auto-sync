# Tag schema

The DB-level shape backing [TAXONOMY.md](TAXONOMY.md)'s category model. PostgreSQL,
same instance as the rest of the app — see
[../photo-server/DATA_DICTIONARY.md](../photo-server/DATA_DICTIONARY.md) for the
non-tag tables (`users`, `photos`, `photo_owners`, etc.) this joins against.
"Now" = already built and live; everything else here is designed, not built — see
[TODO.md](TODO.md) for what's still open before it is.

Supersedes DATA_DICTIONARY.md's old "Future tag schema" sketch (captured
2026-07-18, never designed/committed) and its "Tag dimensions" table outright —
those are folded into this file and TAXONOMY.md, not left as separate stubs.

**Relational, not graph DB** — decision carried over unchanged from the sketch this
supersedes: a graph database earns its cost at a node/edge count and traversal
complexity this project doesn't have (one household, later some invited relatives).
`tags` + `tag_references`, with a discriminator column on the latter, covers every
case below natively in Postgres.

## `tags`

| Column | Status |
| --- | --- |
| id, photo_id, user_id, created_at | now |
| tag (text — the display value, e.g. "Summer 2019", "blurry", "Anna's birthday") | now |
| kind (`album` \| `content`) | now — see the reconciliation note in TODO.md |
| category (one of the 12 in TAXONOMY.md) | designed, not built |
| visibility (`private` \| `shareable`, default `private`) | designed, not built |
| downloaded_at, download_count | now, per (tag, photo) pair |

**Why `downloaded_at`/`download_count` exist**: not usage telemetry for its own
sake — they're the raw signal behind [../VISION.md](../VISION.md) Pillar 2's stated
longer-term goal, "the system suggests photos to remove, learned globally across
the network and personalized per user." Confirmed with Joakim 2026-07-27 as the
priority piece of Pillar 2 to get right now, over the sharing/DFS threads — flagged
here so the field's purpose stays traceable instead of reading as tracking without
a stated reason (raised as a real question, not a rhetorical one, in that session).

`unique(photo_id, user_id, tag)`. The `origin` category is the already-built
`kind='album'` mechanism under a new name — every event tag ([EVENTS.md's](../upload-and-share/EVENTS.md)
QR-driven auto-tag) and upload-batch tag ([UPLOAD.md](../upload-and-share/UPLOAD.md))
is concretely an origin-category tag. `kind='content'` (reserved, no endpoints yet)
was the old free-text manual-tagging path; the new `category` column now carries
that distinction instead, at a finer grain than `content` alone — see TODO.md for
whether `kind` still earns its keep once `category` exists.

Endpoints today (kind='album' only, unaffected by this design):
`GET/POST /tags`, `POST`/`DELETE /tags/{tag}/photos/{photo_id}`,
`GET /tags/{tag}/photos`, `GET /tags/{tag}/download`.

## `entities`

New. One owner-scoped record per recurring person/object/animal/place — the thing a
repeated tag across many photos actually points at, so "my late dog" is one
searchable thing instead of N independently-worded tags. See TAXONOMY.md's "entity
pattern" section for the reasoning.

| Column | Meaning |
| --- | --- |
| id, owner_user_id, created_at | — |
| entity_type | `person` \| `object` \| `animal` \| `place` \| `circle` |
| display_name | "Dad", "my motorcycle", "Bella", "home", "Close Friends" |
| attributes (JSONB) | type-specific: `{species, breed}` for an animal, `{object_type}` for an object, `{place_kind: general\|specific}` for a place, `{member_entity_ids: [...]}` for a circle — empty for a person |
| linked_account_user_id | nullable, **person only** — set once the local record is claimed by/linked to a real account |

One `entities` table with a type discriminator + JSONB attributes, not four
near-identical tables — matches this project's existing polymorphic-column
precedent (`audit_log.details`, `tag_references.reference_value` below) rather than
introducing a new pattern for four things that are structurally the same. **`circle`
added 2026-08-05** ([TAXONOMY.md](TAXONOMY.md)'s "Audience circles"), a fifth
instance of this same shape rather than a fifth pattern: a circle is a named,
owner-scoped record like the other four, it just isn't depicted in any photo — its
members live in `attributes`, not `tag_references`, since a circle is never itself
a photo-content tag (see TAXONOMY.md for why that distinction matters).

## `tag_references`

New. What a tag actually points at — polymorphic, one row can describe an entity
link, a chain to another tag, a pixel region, or an invite email. A single tag can
have more than one reference row (e.g. a co-presence tag: one row per person in the
group).

| Column | Meaning |
| --- | --- |
| id, tag_id (FK → tags.id), created_at | — |
| reference_kind | `entity` \| `tag` \| `pixel_region` \| `email` |
| reference_value | entity id, tag id, or an invite email — meaning depends on `reference_kind` |
| bounding_box | nullable, e.g. `[(23,466),(186,1234)]` — **always independent of whatever `reference_value` points at, never inherited from it** (TAXONOMY.md's relationship rule) |

How each category uses it:

- **People/objects/animals/places**: `reference_kind='entity'`, `reference_value` =
  the entity id, `bounding_box` set if the tag was placed on a specific region of
  the photo.
- **Relationships**: `reference_kind='tag'`, `reference_value` = the tag id being
  qualified (e.g. the dog's animal-tag), plus the relationship tag's own `tag`
  column carries the relation word ("father", "belongs to"). Chains further by a
  relationship tag referencing another relationship tag.
- **Story/narrative**: the story is itself a tag (`category='story_narrative'`);
  other tags/photos join the thread via a `reference_kind='tag'` row pointing at the
  story tag. No separate thread table — reuses the same chaining mechanism.
- **Co-presence/group**: one `reference_kind='entity'` row per person in the group,
  all sharing the same `tag_id`.
- **Unregistered-person invite**: `reference_kind='email'`, `reference_value` = the
  invite address — same shape `pending_shares` already uses for the sharing side of
  this (see [../upload-and-share/SHARING.md](../upload-and-share/SHARING.md)), kept
  as a separate mechanism here since a tag-level invite and a share-level invite are
  triggered from different UI moments even though both resolve the same way.

## `tag_endorsements`

Unchanged from DATA_DICTIONARY.md's reserved definition — moved here as its
authoritative home, not redesigned. Lets a user corroborate another user's tag as a
stronger signal than an unverified single-source one — see
[../upload-and-share/SHARING.md](../upload-and-share/SHARING.md)'s "Tag
verification/endorsement" section for what it's for and why.

| Column | Status |
| --- | --- |
| id, tag_id, endorsing_user_id, created_at | reserved |

`unique(tag_id, endorsing_user_id)`.

## Status

Designed 2026-07-27. No migration, no endpoints. First real implementation decision
this needs before any TDD step: reconciling `kind` against the new `category`
column — see [TODO.md](TODO.md). `entities.entity_type='circle'` added 2026-08-05.
