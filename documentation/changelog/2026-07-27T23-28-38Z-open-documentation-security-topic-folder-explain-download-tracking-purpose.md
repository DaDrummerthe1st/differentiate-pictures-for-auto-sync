# Open documentation/security/ topic folder; explain download-tracking purpose

Joakim asked for the session's scattered security analysis (bounding-box data
sensitivity, dev-environment risk, an open DFS-era facial-recognition question)
organized into a table and saved, not left in chat — opened a new cross-cutting
`security/` topic folder (README + THREATS table + TODO) rather than growing
POLICY.md's hard-rules section into a running log. The DFS-facial-recognition
question is explicitly deferred, not answered — TODO.md carries Joakim's
instruction that it needs real external research from reputable sources, not
guessing. Also closed a loop from earlier in the session: added the actual
purpose behind `downloaded_at`/`download_count` (VISION.md's personalized
photo-curation goal) to SCHEMA.md, since it had no stated "why" before.

- **Doc size**: new `security/README.md` 2070, `security/THREATS.md` 5613,
  `security/TODO.md` 2594 chars. `documentation/README.md` 1547 → 1717 (+170,
  index entry). `policies/POLICY.md` 7256 → 7463 (+207, cross-reference).
  `tags/SCHEMA.md` 6104 → 6685 (+581, download-tracking purpose note).
