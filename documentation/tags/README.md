# documentation/tags/

The tag taxonomy — cross-cutting, like [policies/](../policies/README.md), not a
feature folder tied to one branch. Every topic that touches tagging
([photo-server/](../photo-server/README.md)'s built `kind='album'` mechanism,
[upload-and-share/](../upload-and-share/README.md)'s ownership/sharing/event
design) references *into* this folder for what a tag actually is, rather than
each defining its own piece of it. A tag is a foundation the rest of the app's
metadata/search/sharing model builds on — not necessarily the only one, but one
significant enough to need a single, authoritative home instead of being scattered
across whichever topic happened to need a tag first.

| File | What's there |
| --- | --- |
| [TAXONOMY.md](TAXONOMY.md) | The category model — 12 tag categories, the shared entity pattern (people/objects/animals/places), the relationship-chaining rule, the two-tier visibility model, and how search walks the relationship graph. Start here. |
| [SCHEMA.md](SCHEMA.md) | The DB-level shape: `tags`, `entities`, `tag_references`, `tag_endorsements`. |
| [UX_FLOWS.md](UX_FLOWS.md) | Interaction-level detail: bounding-box tagging, the invite CTA, the blur-preview sharing review. |
| [TODO.md](TODO.md) | Open, not-designed-now items — a user bio for tag suggestions, contacts import, nudity auto-detection, entity dedup, and more. |

How automated tags actually get proposed (detector models, the embedding index, the explanation/
correction layer) lives in [../curation/README.md](../curation/README.md), not here — this folder
owns what a tag *means*, curation/ owns how one gets suggested automatically.

Visual mockup: [prototypes/mockup/](../../previous-work/multi-user-web-app/prototypes/mockup/README.md), same
in-memory-fake-database convention as
[upload-and-share-mockup/](../../previous-work/multi-user-web-app/prototypes/upload-and-share-mockup/README.md) —
a real clickable prototype covering all 12 categories, not a re-rendering of this
written design. Illustrative UI only, no schema/endpoints implied.

## Status

**Next session needing tag context starts here, not with a repeat multi-file
survey** — before this folder existed, reconstructing "everything about tags"
meant reading 9 separate files across two topic folders (done once, by hand, to
open this design pass). That cost doesn't recur now; extend the 4 files above
directly.

Opened 2026-07-27 (branch `tags`), consolidating tag-related content that was
previously scattered across `photo-server/DATA_DICTIONARY.md` and several
`upload-and-share/` files. Design only — no schema migration, no endpoints. See
each file's own Status line for specifics.

**2026-08-05**: a narrowed, build-ready slice of this design (people/places/objects/animals + a
free-text catch-all, no entities/relationships/sharing) is now actually built, in `app/`'s own
lightweight SQLite table rather than this file's Postgres design — see
[SCHEMA.md](SCHEMA.md)'s "Now" section and [../gui/README.md](../gui/README.md)'s Tags feature entry.
This folder's own design docs are otherwise unchanged by that build.
