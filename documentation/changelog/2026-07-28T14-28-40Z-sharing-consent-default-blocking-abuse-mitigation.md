# Sharing consent default, blocking, abuse mitigation

Added `upload-and-share/ABUSE_MITIGATION.md`: mutual-acceptance-by-default for receiving a share (closing a real gap — the username path previously created the ownership row with no consent step at all), a per-user `open` opt-out gated behind an as-yet-unbuilt nudity/NCII classifier, and a `blocked_users` mechanism. Cross-identity fingerprinting for repeat-blocked users was considered and rejected (contradicts the project's own closed-by-default privacy stance, poor technical trade at this project's actual scale) — recorded, not left as an open question.

- **Doc size** (Unicode codepoints): `upload-and-share/ABUSE_MITIGATION.md` 0 → 4357 (new); `upload-and-share/SHARING.md` 4497 → 4997; `upload-and-share/README.md` 3137 → 3277; `upload-and-share/TODO.md` 1118 → 1608.
