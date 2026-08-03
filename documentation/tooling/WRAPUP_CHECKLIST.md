# wrapup_checklist

Moved here from `tools/wrapup_checklist/README.md`, per [CLAUDE.md](../../CLAUDE.md)'s documentation-layout rule. Code stays at `tools/wrapup_checklist/`.

**Purpose:** raised in [TODO.md](TODO.md) 2026-07-19 — the session wrap-up checklist in [README.md](README.md)'s table relied on a session reading and remembering it correctly every time, the same failure mode that motivated `commit_cost`'s own `check_coverage.sh` (see [COMMIT_COST.md](COMMIT_COST.md) — three commits had silently never gotten a logged cost row). This generalizes that same "actually check, don't just remember" idea across the whole table, not just commit_cost's row.

## What it actually mechanizes — and what it can't

Of the checklist table's rows, only some have a trigger condition a script can evaluate at all:

| Check | How it's verified |
| --- | --- |
| `commit_cost` coverage | every commit has a row in `commit_costs.jsonl` (same logic `check_coverage.sh` already used, reused here rather than re-implemented) |
| `doc_metrics` coverage | every commit that touched a `*.md` file has a row in `metrics.jsonl` |
| Pre-commit hooks installed | `git config core.hooksPath` is set to `.githooks` (so the `app/tests` and `secrets_scan` gates actually run) |
| Dead-link sweep / topic-folder `TODO.md` presence | delegates to `tools/documentation_checks/run.py` rather than re-implementing it |

Both coverage checks skip the current HEAD commit — logging happens *after* committing (documented in [COMMIT_COST.md](COMMIT_COST.md)), so HEAD is expected to be unlogged mid-session, same as `check_coverage.sh`'s own documented exception.

Everything else in the table — `server/tests`, a changelog entry, lockfile consistency, Docker hygiene, the doc-drift check, the wider sweep, loose ends in chat, the stale-TODO glance, the forward-effectiveness note — has a trigger condition that needs either judgment ("was this a meaningful change") or session-scoped context a script run after the fact can't see ("did `docker build` run this session"). These print unconditionally as reminders, never pass/fail — the point is that a session still has to look, not that a script decides for them. Same scoping precedent as [DOCUMENTATION_CHECKS.md](DOCUMENTATION_CHECKS.md): mechanize the mechanical subset, still do the real pass.

## Files

- `tools/wrapup_checklist/checks.py` — pure logic (which commits are missing a row, whether hooks are configured, which commits touched markdown). Tested in `test_checks.py`.
- `tools/wrapup_checklist/run.py` — CLI. Gathers real git/jsonl state, calls the pure checks, shells out to `documentation_checks/run.py`, then prints the judgment-call reminders.

## Running it

```
python3 -m unittest tools.wrapup_checklist.test_checks -v   # tests
python3 tools/wrapup_checklist/run.py                          # run the checklist
```

Exit code `1` if any mechanical check found something outstanding; `0` otherwise. The judgment-call reminders never affect the exit code.
