# Trim tag_endorsements redundancy between SCHEMA.md and SHARING.md

`tools/redundancy_scan` flagged a 28-word verbatim overlap between SCHEMA.md and
SHARING.md's tag_endorsements rationale, introduced by this session's own edits —
fixed per CLAUDE.md's "cross-reference before redundancy" rule: SHARING.md keeps
the rationale, SCHEMA.md just points to it.

- **Doc size**: `documentation/tags/SCHEMA.md` — 6084 → 6058 chars.
