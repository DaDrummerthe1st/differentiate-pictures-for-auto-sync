# prototypes/mockup/

Documented in [documentation/tags/README.md](../../documentation/tags/README.md) — all
documentation lives under `documentation/`, per [CLAUDE.md](../../CLAUDE.md)'s
documentation-layout rule.

Static HTML/CSS/JS only, no server, nothing hosted externally, no build step — open
`index.html` directly in a browser, or `python3 -m http.server` from this folder.

Real clickable prototype, same convention as
[prototypes/upload-and-share-mockup/](../upload-and-share-mockup/README.md): an
in-memory fake database (seeded entities, tags, tag references, photos) that actual
clicks mutate, not static cards. Showcases every one of TAXONOMY.md's 12 tag
categories against 10 seed photos — bounding-box tagging with a person/local-vs-linked
badge, the invite CTA for an unregistered person, entity-owned relationship chaining
(2 hops deep, e.g. searching "Pappa" surfaces his dog's, motorcycle's, and home's
photos, plus a photo with no direct connection reached only via a second hop), the
privacy category forcing a tag private regardless of the photo's other tags, and the
blur-preview review before sharing any tag as an album. The **Kategorier** tab is a
clickable legend of all 12 categories, cross-linking into the gallery.

Two illustrative simplifications versus the real design, called out in a comment at
the top of `script.js`: a relationship tag here carries two explicit reference rows
(subject + object) rather than SCHEMA.md's single "tag being qualified" reference —
allowed by SCHEMA.md's own "a tag can have more than one reference row" rule, not a
deviation from it; and the search graph walks `entities`, not raw tag IDs, per
TAXONOMY.md's explicit statement that the entity is what search should match against.

No schema migration, no endpoints implied — illustrative UI only, same as the
upload-and-share mockup.
