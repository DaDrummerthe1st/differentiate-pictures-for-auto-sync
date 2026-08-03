# wrapup_checklist

Moved here from `tools/wrapup_checklist/README.md`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule. Code stays at `tools/wrapup_checklist/`.

**Purpose:** raised in [TODO.md](TODO.md) 2026-07-19 — the session wrap-up checklist in [README.md](README.md)'s table relied on a session reading and remembering it correctly every time, the same failure mode that originally motivated `commit_cost`'s own `check_coverage.sh` (see [COMMIT_COST.md](COMMIT_COST.md) — three commits had silently never gotten a logged cost row). This generalizes that same "actually check, don't just remember" idea across the whole table, not just commit_cost's row — and since 2026-08-03 (see "Scaling" below) is also the *sole* implementation of both ledgers' coverage checks, the standalone `check_coverage.sh` scripts having been retired.

## What it actually mechanizes — and what it can't

Of the checklist table's rows, only some have a trigger condition a script can evaluate at all:

| Check | How it's verified |
| --- | --- |
| `commit_cost` coverage | every commit has a row in `commit_costs.jsonl` |
| `doc_metrics` coverage | every commit that touched a `*.md` file has a row in `metrics.jsonl` |
| Pre-commit hooks installed | `git config core.hooksPath` is set to `.githooks` (so the `app/tests` and `secrets_scan` gates actually run) |
| Dead-link sweep / topic-folder `TODO.md` presence | delegates to `tools/documentation_checks/run.py` rather than re-implementing it |

Both coverage checks skip the current HEAD commit in full-checklist mode — logging happens *after* committing (documented in [COMMIT_COST.md](COMMIT_COST.md)), so HEAD is expected to be unlogged mid-session. `--coverage-only` mode (used by the pre-commit hook, see below) doesn't skip HEAD — it runs *before* the new commit exists, so `git log` at that point already ends at the previous, by-then-logged commit.

## Scaling

Retired 2026-08-03: the original `tools/doc_metrics/check_coverage.sh` and `tools/commit_cost/check_coverage.sh` shell scripts each `grep`-checked the whole ledger file once *per commit* (and `doc_metrics`'s additionally ran `git ls-tree` per commit) — runtime that grows faster than commit count, and JSON-as-text grepping that a reformatted line or a renamed key would silently misread rather than fail on. `run.py` instead makes exactly one `git log` call for all commit hashes, one more for all changed-files-by-commit, and one parsed pass (`checks.logged_keys()`, real `json.loads`, no `.get()`/swallowing) over each jsonl — cost is one git call plus one file pass, not one per commit, and a renamed/reshaped ledger column raises loudly instead of reporting a false gap. `tools/wrapup_checklist/test_run.py` pins the call-count invariant (mocked at 5,000 simulated commits) so a regression back to a per-commit call fails a test immediately rather than only showing up as a slowdown once the repo is actually that large — this is reasoned about and guarded by a test, not measured against a real 10x-scale copy of the repo, since none exists to benchmark against.

## Enforcement

`--coverage-only` (just the two ledger checks, skipping the dead-link sweep and judgment-call reminders) runs automatically, blocking, from `.githooks/pre-commit` right after the `app/tests` and secrets-scan gates — so a logging gap is caught at the very next commit attempt instead of depending on a session remembering to run the full checklist at close. The full checklist (this document) is still the one that should run at session close, for the checks `--coverage-only` intentionally skips.

Everything else in the table — `server/tests`, a changelog entry, lockfile consistency, Docker hygiene, the doc-drift check, the wider sweep, loose ends in chat, the stale-TODO glance, the forward-effectiveness note — has a trigger condition that needs either judgment ("was this a meaningful change") or session-scoped context a script run after the fact can't see ("did `docker build` run this session"). These print unconditionally as reminders, never pass/fail — the point is that a session still has to look, not that a script decides for them. Same scoping precedent as [DOCUMENTATION_CHECKS.md](DOCUMENTATION_CHECKS.md): mechanize the mechanical subset, still do the real pass.

## Files

- `tools/wrapup_checklist/checks.py` — pure logic (which commits are missing a row, whether hooks are configured, which commits touched markdown, parsing a ledger's jsonl lines via `logged_keys()`). Tested in `test_checks.py`.
- `tools/wrapup_checklist/run.py` — CLI. Gathers real git/jsonl state via a single `git log` call per query (see "Scaling"), calls the pure checks, shells out to `documentation_checks/run.py` in full-checklist mode, then prints the judgment-call reminders. Tested in `test_run.py` (the git-call-count scaling guard — not the checks themselves, which are covered in `test_checks.py`).

## Running it

```
python3 -m unittest tools.wrapup_checklist.test_checks tools.wrapup_checklist.test_run -v   # tests
python3 tools/wrapup_checklist/run.py                          # full checklist, session close
python3 tools/wrapup_checklist/run.py --coverage-only          # ledger coverage only, what pre-commit runs
```

Exit code `1` if any mechanical check found something outstanding; `0` otherwise. The judgment-call reminders never affect the exit code.
