# Build a real clickable upload-and-share mockup, not styled docs

Two earlier attempts today just re-rendered OWNERSHIP/UPLOAD/SHARING/EVENTS.md as styled cards — no seed data, no state. `prototypes/upload-and-share-mockup/` now has an actual tabbed app (Gallery/Upload/Sharing/Events) reusing `app/static/`'s dark theme, backed by an in-memory fake database that real clicks mutate: switching the "Viewing as" user shows a share made as one account become pending/active for the other. Verified end-to-end with a headless-Chrome Selenium run (gallery, cross-user share visibility, upload, event curation, guest upload) — 15/15 checks passed, no console errors, before committing.

- **Doc size**: `documentation/upload-and-share/README.md` 2854 → 3137 chars (+283, points at the new prototype and updates the "no visual mockup exists" note).
