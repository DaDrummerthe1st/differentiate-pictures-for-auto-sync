# tooling/ — open work

- **Compact per-run test-result ledger**, same shape as `doc_metrics`/
  `commit_cost` (one append-only row per run: suite, pass/fail/skip
  counts, duration, commit hash). Raised 2026-07-18: neither pytest
  suite's results are tracked over time anywhere - each run is only
  ever observed live in the terminal. Useful for spotting trends (suite
  getting slower, a test flaking intermittently) - not a substitute for
  `documentation/bugs/reports/`'s per-investigation logs, which already
  serve the separate need of a future session understanding *how* a
  past debugging session reasoned through a live issue. Not started.
