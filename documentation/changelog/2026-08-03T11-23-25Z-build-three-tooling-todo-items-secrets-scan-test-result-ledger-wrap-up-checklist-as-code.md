# Build three tooling TODO items: secrets scan, test-result ledger, wrap-up checklist as code

Built the three build-ready items from `tooling/TODO.md` (the other two — real-database consolidation, no-shorthand-names — are open design/policy questions, left as-is). `tools/secrets_scan/` mechanizes the manual secrets-in-diff scan raised 2026-07-28, now blocking `.githooks/pre-commit` on any high-confidence finding. `tools/test_results/` gives `app/tests`/`server/tests` the same append-only jsonl trend-tracking `doc_metrics`/`commit_cost` already have. `tools/wrapup_checklist/` mechanizes the mechanical subset of README.md's wrap-up table (commit_cost/doc_metrics coverage, pre-commit-hook install, delegating to `documentation_checks`); running it surfaced a real pre-existing gap — 30 `*.md`-touching commits with no logged `doc_metrics` row — flagged in TODO.md, not fixed here.

- **Doc size**: 9 files combined 21,507 → 32,919 chars (+11,412).
