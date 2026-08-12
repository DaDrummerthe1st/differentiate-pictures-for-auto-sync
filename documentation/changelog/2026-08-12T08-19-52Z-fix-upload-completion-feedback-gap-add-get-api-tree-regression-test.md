# Fix upload-completion feedback gap, add GET /api/tree regression test

Root-caused the 2026-08-08 "uploaded picture doesn't show up" report: `/api/upload` always worked,
the frontend just gave no visible confirmation. `app.js` now shows an explicit alert after a batch
finishes. Added `test_uploaded_photo_becomes_visible_via_api_tree` since nothing previously asserted
`/api/tree` reflects an upload.

- **Doc size**: `documentation/GLOSSARY.md` +643 chars, `documentation/curation/TODO.md` -897 chars
  (closed out the now-resolved bug writeup).
