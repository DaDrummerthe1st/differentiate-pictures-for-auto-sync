# prototypes/upload-and-share-mockup/

Documented in [documentation/upload-and-share/README.md](../../documentation/upload-and-share/README.md) — all documentation lives under `documentation/`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule.

Static HTML/CSS/JS only, no server, nothing hosted externally, no build step — open `index.html` directly in a browser, or `python3 -m http.server` from this folder.

Real clickable prototype: an in-memory fake database (seeded users, photos, tags, shares) that actual clicks mutate, not static cards. Switch the "Viewing as" user in the header to see the same state from a different account's perspective (a share made as one user shows up as a pending/active share for the other).
