# test_results

Moved here from `tools/test_results/README.md`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule. Code stays at `tools/test_results/`.

**Purpose:** a durable, append-only ledger of what each pytest run actually produced (suite, pass/fail/error/skip counts, duration, commit hash) — raised in [TODO.md](TODO.md) 2026-07-18, because neither `app/tests` nor `server/tests` had their results tracked over time anywhere; each run was only ever observed live in the terminal, with no way to spot a suite getting slower or a test flaking intermittently after the fact. Same append-only jsonl shape as [DOC_METRICS.md](DOC_METRICS.md)/[COMMIT_COST.md](COMMIT_COST.md), tracking a different axis (test health, not doc size or token cost).

**Not a substitute for** `documentation/bugs/repo/under_process/`'s per-investigation logs, which serve the separate need of a future session understanding *how* a past debugging session reasoned through a live issue — this only tracks the numbers.

## How it works

`tools/test_results/log.py --suite <app|server>` runs the named suite with pytest's own built-in `--junitxml` flag (no plugin required), parses the resulting XML for `tests`/`failures`/`errors`/`skipped`/`time`, and appends one row to `tools/test_results/test_runs.jsonl`. `passed` is always derived (`tests - failures - errors - skipped`) — junit xml has no separate field for it.

- **`app`** runs `python3 -m pytest app/tests -q` from the repo root (fast, in-process).
- **`server`** runs `uv run pytest tests -q` from `server/`, per [documentation/photo-server/TOOLCHAIN.md](../photo-server/TOOLCHAIN.md)'s documented default command — this excludes docker-marked tests and doesn't bring up the Postgres/Redis containers itself. Bring those up yourself first (`server/scripts/test_db.sh up` / `test_redis.sh up`) if the run needs to cover DB/Redis-touching tests.

Every run is logged regardless of outcome — `log.py` exits with pytest's own exit code, so a CI-style caller still sees failure, but the ledger gets the row either way. A failing run is exactly as important to have on record as a passing one.

## Files

- `tools/test_results/metrics.py` — pure logic (junit XML parsing, row construction). Tested in `test_metrics.py`.
- `tools/test_results/log.py` — CLI. Runs a suite, appends a row.
- `tools/test_results/report.py` — CLI. Prints one line per logged run; `--suite app`/`--suite server` filters to one suite.
- `tools/test_results/test_runs.jsonl` — append-only, **git-tracked**, per CLAUDE.md's self-sufficiency rule. Doesn't exist until `log.py` runs for the first time — there's no way to backfill past runs' pass/fail counts retroactively, since nothing junit-shaped was ever produced for them (same one-way-forward-only situation `doc_metrics`' one-commit lag documents, just with no `--backfill` possible at all here).

## Running it

```
python3 -m unittest tools.test_results.test_metrics -v   # tests
python3 tools/test_results/log.py --suite app              # after running app/tests
python3 tools/test_results/log.py --suite server            # after running server/tests
python3 tools/test_results/report.py                         # see the trend
python3 tools/test_results/report.py --suite app             # filtered to one suite
```
