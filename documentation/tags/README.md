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

## Status

Opened 2026-07-27 (branch `tags`), consolidating tag-related content that was
previously scattered across `photo-server/DATA_DICTIONARY.md` and several
`upload-and-share/` files. Design only — no schema migration, no endpoints. See
each file's own Status line for specifics.
