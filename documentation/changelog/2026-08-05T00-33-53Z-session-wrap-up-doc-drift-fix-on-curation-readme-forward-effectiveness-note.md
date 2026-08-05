# Session wrap-up: doc-drift fix on curation README, forward-effectiveness note

Ran `tools/wrapup_checklist/run.py` (mechanical checks: commit_cost/doc_metrics coverage, hook installation, dead-link sweep — all clean after catching up one commit_cost row) plus the judgment-call pass: no code touched this session so `server/tests`/lockfile/Docker checks don't apply; changelog entries already existed per meaningful change; no loose ends or stale-marked-open items found. One real doc-drift catch: `curation/README.md`'s Status line hadn't mentioned this session's ARCHITECTURE.md split — fixed, with the forward-effectiveness framing made explicit (same win as tags/README.md's own earlier split: a session needing only identity-matching/scoring no longer reads the full pipeline explanation to get there).

- **Doc size**: `documentation/curation/README.md` — +479 chars (Unicode codepoints, per DOC_METRICS.md methodology).
