# Detector upload-size guard and Pillow dependency bump (wrap-up sweep)

Session wrap-up sweep (per WORKFLOW.md's "widen the sweep past docs" step) on files touched this
session found two real gaps, both fixed same-session rather than just flagged: (1) `detector/main.py`'s
new `POST /detect` had no upload-size cap — `MAX_UPLOAD_BYTES` (25MB default, env-overridable via
`DETECT_MAX_UPLOAD_BYTES`) now rejects an oversized body in capped chunks before a full read/decode,
TDD'd (`test_detect_rejects_an_oversized_upload`), documented as THREATS.md #16; (2) `pillow` was
pinned to a stale 11.3.0 in both `requirements.txt` and `detector/requirements.txt` — checked PyPI
(current release: 12.3.0), bumped both, full suite (111 tests) re-verified green against it before
pinning, per WORKFLOW.md's dependency-freshness rule. Also cleared ~12GB of reclaimable Docker build
cache (`docker builder prune`) at Joakim's explicit request — image/volume pruning held off since
`docker images` showed other unrelated projects (`buzzkit-api`, `gnucash`) sharing this daemon.

- **Doc size**: `documentation/security/THREATS.md` +982 chars.
- **Doc size**: `documentation/curation/TODO.md` +539 chars.
