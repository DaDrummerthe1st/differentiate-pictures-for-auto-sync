# Future-proof commit_cost/doc_metrics coverage checks

Retired the two per-ledger `check_coverage.sh` shell scripts (per-commit grep, quadratic-ish) in favor of `tools/wrapup_checklist`'s single tested implementation, wired blocking into `.githooks/pre-commit` via a new `--coverage-only` mode. Also merged `master`'s tooling-todo-investigation branch (secrets_scan, test_results, wrapup_checklist) into `curation`, which had forked before that merge.

- **Doc size**: +4,608 chars across `DOC_METRICS.md`, `COMMIT_COST.md`, `README.md`, `TODO.md`, `WRAPUP_CHECKLIST.md`.
