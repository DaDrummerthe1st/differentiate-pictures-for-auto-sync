# tooling/

Documentation for project-wide utilities under `tools/` — not tied to any single topic (`picture-handling/`, `photo-server/`, `distributed-sync/`), so they live here rather than in one of those folders. See [TODO.md](TODO.md) for open work.

| File | What's there |
| --- | --- |
| [DOC_METRICS.md](DOC_METRICS.md) | `tools/doc_metrics/` — tracks documentation char-count growth per commit, tied to a `task` label |
| [COMMIT_COST.md](COMMIT_COST.md) | `tools/commit_cost/` — exact real token/dollar cost per commit, from Claude Code's own session transcripts |
| [CLEANING.md](CLEANING.md) | Full, on-demand documentation audit — goals and methodology, not a per-session check |
| [DOCUMENTATION_CHECKS.md](DOCUMENTATION_CHECKS.md) | `tools/documentation_checks/` — the mechanical subset of a CLEANING.md pass (dead links, topic-folder `TODO.md` presence), scripted so it isn't rewritten ad hoc each time |
| [REDUNDANCY_SCAN.md](REDUNDANCY_SCAN.md) | `tools/redundancy_scan/` — surfaces markdown phrases repeated verbatim across files, candidates for a CLEANING.md pass's cross-reference/compaction step |
| [SECRETS_SCAN.md](SECRETS_SCAN.md) | `tools/secrets_scan/` — grep-based secrets-in-diff scan, wired into `.githooks/pre-commit` |
| [TEST_RESULTS.md](TEST_RESULTS.md) | `tools/test_results/` — append-only ledger of pytest pass/fail/skip counts and duration per run, same shape as `doc_metrics`/`commit_cost` |
| [WRAPUP_CHECKLIST.md](WRAPUP_CHECKLIST.md) | `tools/wrapup_checklist/` — runs the mechanical subset of the session wrap-up checklist below as code instead of relying on memory |

## Session wrap-up checklist

Every check an AI session working in this repo is expected to run before calling a session done, collected in one place — some are defined in this project's own [CLAUDE.md](../../CLAUDE.md), some in Joakim's cross-project `~/.claude/CLAUDE.md` (marked "global" below; that file applies to every project he works in, so its wording stays generic there — this table is the project-specific copy for quick reference, not a second source of truth to edit independently).

Each check has a trigger condition. Most only apply when something specific happened this session — run the check if the condition is true, skip it (not "run it and find nothing") if it isn't. Decided 2026-07-19: previously every check ran on every session regardless, which made wrap-up itself take about as long as the work it was closing out.

| Check | Trigger | Source |
| --- | --- | --- |
| `app/tests` (fast, in-process) | before every commit, docs-only or not | local, mechanically enforced by `.githooks/pre-commit` — see below |
| `server/tests` (container-based) | every commit touching `server/`/`app/` code; for a doc-only commit, only if it hasn't already run clean this session against the same code | local |
| Secrets-in-diff scan | before every commit | local, mechanically enforced by `.githooks/pre-commit` via `tools/secrets_scan/` (see [SECRETS_SCAN.md](SECRETS_SCAN.md)) — see below |
| `test_results` logging | after each `app/tests`/`server/tests` run, if tracking that run's trend is useful | local, see [TEST_RESULTS.md](TEST_RESULTS.md) |
| `doc_metrics` logging | every commit touching a `*.md` file | local |
| `commit_cost` logging | every commit | local |
| Changelog entry | every meaningful change | local |
| `commit_cost`/`doc_metrics` coverage check | every session close | local, mechanized by `tools/wrapup_checklist/run.py` (see [WRAPUP_CHECKLIST.md](WRAPUP_CHECKLIST.md)) — covers what `tools/commit_cost/check_coverage.sh` used to check alone, plus `doc_metrics`, pre-commit-hook installation, and delegates to `documentation_checks` for the dead-link sweep below |
| Lockfile/manifest consistency | only if a manifest file changed this session | global |
| Docker hygiene (dangling/abandoned images) | only if `docker build`/`compose build` ran this session | global |
| Cross-reference link check | only if a "see X" doc link was touched this session | global |
| Doc-drift check (status lines/TODO/specs vs. code) | only if code or docs changed this session | global |
| Wider sweep (stale dependency versions, dead code, stale TODO/FIXME references, security gaps) | scoped to files touched this session | global |
| Loose ends in the chat (unanswered questions, dropped "I'll get back to you" threads, unresolved TBDs) | every session close | global |
| Stale-TODO glance (items already resolved but still marked open) | every session close | global |
| Forward-effectiveness note (one concrete note on what would make the next session cheaper) | every session close | global |
| Systematic security-discovery pass (`pip-audit`, OWASP ZAP scan — see [PHOTO_SERVER's TODO.md](../photo-server/TODO.md)) | not diff-triggered — audits the live deployed surface, not a change; needs a real recurring schedule once built, not a per-session check | local, not built yet |

## Pre-commit hook (`app/tests` + secrets scan, mechanically enforced)

Added 2026-07-27 after an AI session committed twice in a row without running
`app/tests` first, despite the rule above already saying to
(see `documentation/bugs/claude-bugs/`) — wording alone wasn't enough, so this
makes the fast-suite-before-commit rule self-enforcing instead of
memory-dependent. `.githooks/pre-commit` runs `app/tests` and blocks the commit
on failure; it only reminds (doesn't block) about `server/tests` when a commit
touches `server/`/`app/`, since that suite is container-based, slower, and the
rule's "skip if already run clean this session" judgement call isn't
mechanically checkable.

The same hook then runs `tools/secrets_scan/run.py` (added 2026-08-03, per
[TODO.md](TODO.md)'s 2026-07-28 item) and blocks the commit on any finding —
see [SECRETS_SCAN.md](SECRETS_SCAN.md) for what it checks and why a
generic "password=" heuristic was deliberately left out.

**Not active by default** — git doesn't read hooks from a repo-tracked
directory on its own. One-time setup, per clone:

```
git config core.hooksPath .githooks
```

This changes local git config, so it's a command to run yourself, not
something an AI session runs on your behalf (see CLAUDE.md's git safety
protocol) — hand it over once per clone.

**Persistent nudge, not a one-time flag**: once a session shows drift (a second, unrelated concern enters the conversation) or has clearly run long, say so plainly in every subsequent message until the session actually ends — starting as soon as the signal appears, not at a context-limit warning. This is a nudge Joakim decides whether to act on, not a hard stop. Decided 2026-07-19 after wrap-up itself had grown open-ended enough that ending a session took about as long as the work that preceded it (see [documentation/bugs/claude-bugs/under_process/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md](../bugs/claude-bugs/under_process/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md)).
