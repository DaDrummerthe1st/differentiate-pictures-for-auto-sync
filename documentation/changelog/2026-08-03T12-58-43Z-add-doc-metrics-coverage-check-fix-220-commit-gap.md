# Add doc_metrics coverage check, fix a 220-commit silent logging gap

Discovered while logging doc_metrics/commit_cost for this session's own commits: `tools/doc_metrics/log.py --backfill` found 220 previously-unlogged commits (251 of 474 had a row; 471 after backfill — the remaining 3 predate any `.md` file existing). `commit_cost/check_coverage.sh` (added 2026-07-17) never caught this because it only checks `commit_costs.jsonl`, not `metrics.jsonl` — the original fix covered one of the two logging tools its own bug report names, not both.

Added `tools/doc_metrics/check_coverage.sh`, mirroring `commit_cost`'s, wired into the wrap-up checklist as its own row. Reopened-then-refixed `documentation/bugs/claude-bugs/fixed/2026-07-17-missed-commit-cost-logging-for-3-commits.md` with a "Recurrence #1" section rather than filing a new bug, per this project's own recurrence rule.

- **Doc size**: +~2,700 chars (net, across DOC_METRICS.md, tooling/README.md, and the bug file).
