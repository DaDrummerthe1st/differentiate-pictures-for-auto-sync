# Fix false-positive dead-link check on quote-wrapped [X](path) idiom

`find_broken_links` only excluded illustrative `[X](path)` link examples inside backticks; extended to the exact same literal pair outside backticks too, fixing both real false positives (a 2026-08-02 changelog entry and this bug file's own description of the bug). See fixed/2026-08-03-...-SOLVED.md.

- **Doc size**: +2,526 chars (bug file move + resolution write-up).
