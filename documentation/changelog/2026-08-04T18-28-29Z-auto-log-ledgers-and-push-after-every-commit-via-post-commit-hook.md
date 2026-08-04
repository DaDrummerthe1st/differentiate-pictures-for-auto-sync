# Auto-log ledgers and push after every commit via post-commit hook

New `.githooks/post-commit` runs `doc_metrics`/`commit_cost` `log.py` after every commit, auto-commits any new rows separately, and pushes (publishing a new branch if needed) — closing the pre-commit coverage gate's bounce-and-retry loop at the source, per Joakim's request that push always follow commit authorization.

- **Doc size**: +2,893 chars across `README.md`, `DOC_METRICS.md`, `COMMIT_COST.md`.
