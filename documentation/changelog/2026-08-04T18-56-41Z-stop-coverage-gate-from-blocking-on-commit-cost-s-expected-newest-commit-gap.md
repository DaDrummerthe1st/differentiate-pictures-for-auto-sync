# Stop coverage gate from blocking on commit_cost's expected newest-commit gap

The previous fix made commit_cost's newest-commit gap permanent and expected, but the coverage gate didn't know that — it blocked the hook's own next auto-commit attempt. `check_coverage()` now always excludes commit_cost's newest hash (doc_metrics keeps its existing exclusion, unaffected).

- **Doc size**: no `*.md` files changed (code only).
