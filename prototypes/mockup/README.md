# prototypes/mockup/

Documented in [documentation/tags/UX_FLOWS.md](../../documentation/tags/UX_FLOWS.md) — all documentation lives under `documentation/`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule.

Static HTML/CSS/JS only, no server, nothing hosted externally, no build step — open `index.html` directly in a browser, or `python3 -m http.server` from this folder.

Real clickable prototype, same convention as [prototypes/upload-and-share-mockup/](../upload-and-share-mockup/README.md): an in-memory fake database (seeded entities, tags, tag references, photos) that actual clicks mutate, not static cards. No schema migration, no endpoints implied — illustrative UI only.
