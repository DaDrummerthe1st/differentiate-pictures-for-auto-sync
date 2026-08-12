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
| `doc_metrics` logging | every commit touching a `*.md` file | local, mechanically enforced by `.githooks/post-commit` — see below |
| `commit_cost` logging | every commit | local, mechanically enforced by `.githooks/post-commit` — see below |
| Changelog entry | every meaningful change | local |
| `commit_cost`/`doc_metrics` coverage check | before every commit | local, mechanically enforced by `.githooks/pre-commit` via `tools/wrapup_checklist/run.py --coverage-only` — see below. Full `run.py` (session close) additionally checks pre-commit-hook installation and delegates to `documentation_checks` for the dead-link sweep; see [WRAPUP_CHECKLIST.md](WRAPUP_CHECKLIST.md) |
| Lockfile/manifest consistency | only if a manifest file changed this session | global |
| Docker hygiene (dangling/abandoned images) | only if `docker build`/`compose build` ran this session | global |
| Cross-reference link check | only if a "see X" doc link was touched this session | global |
| Doc-drift check (status lines/TODO/specs vs. code) | only if code or docs changed this session | global |
| Wider sweep (stale dependency versions, dead code, stale TODO/FIXME references, security gaps) | scoped to files touched this session | global |
| Loose ends in the chat (unanswered questions, dropped "I'll get back to you" threads, unresolved TBDs) | every session close | global |
| Stale-TODO glance (items already resolved but still marked open) | every session close | global |
| Forward-effectiveness note (one concrete note on what would make the next session cheaper) | every session close | global |
| Systematic security-discovery pass (`pip-audit`, OWASP ZAP scan — see [PHOTO_SERVER's TODO.md](../photo-server/TODO.md)) | not diff-triggered — audits the live deployed surface, not a change; needs a real recurring schedule once built, not a per-session check | local, not built yet |

## Pre-commit hook (`app/tests` + secrets scan + ledger coverage, mechanically enforced)

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

Finally the hook runs `tools/wrapup_checklist/run.py --coverage-only` and
blocks the commit if either `commit_cost` or `doc_metrics` has a commit
missing a logged row — retiring the two standalone `check_coverage.sh`
scripts that used to only run when a session remembered to at wrap-up (see
[WRAPUP_CHECKLIST.md](WRAPUP_CHECKLIST.md)'s "Scaling" and "Enforcement"
sections for why this closes that gap and how it stays fast as the repo
grows).

**If this gate blocks a commit that already has files staged** (as opposed to the fully-automatic
post-commit catch-up below, which always runs against a clean-except-ledger index by construction):
run `tools/commit_cost/log.py` and/or `tools/doc_metrics/log.py` to catch up, then commit the
ledger file(s) alone with one of the three recognized catch-up titles ("Log doc metrics and commit
cost for the previous commit", "Log commit cost for the previous commit", "Log doc metrics for the
previous commit"), then re-stage and commit the real change separately.

This used to depend on manually running a `git status`/`grep` one-liner before every catch-up
commit - it recurred twice anyway (see
[documentation/bugs/claude-bugs/](../bugs/claude-bugs/README.md)), the second time because the
documented one-liner itself silently lied: this repo's `grep` (via Claude Code's own shell-function
shim around `ugrep`) returns the wrong exit code for `-q` combined with `-v`, so
`grep -qv 'commit_costs.jsonl\|metrics.jsonl'` reported "clean" even with unrelated files staged,
regardless of whether it was actually run. **`.githooks/commit-msg`** now enforces this
mechanically instead - it inspects the real staged diff against the commit message and refuses any
of the three catch-up titles above unless the diff is *exclusively* the ledger file(s), so there's
no longer a manual check to remember or to get wrong.

**Not active by default** — git doesn't read hooks from a repo-tracked
directory on its own. One-time setup, per clone:

```
git config core.hooksPath .githooks
```

This changes local git config, so it's a command to run yourself, not
something an AI session runs on your behalf (see CLAUDE.md's git safety
protocol) — hand it over once per clone.

**Persistent nudge, not a one-time flag**: once a session shows drift (a second, unrelated concern enters the conversation) or has clearly run long, say so plainly in every subsequent message until the session actually ends — starting as soon as the signal appears, not at a context-limit warning. This is a nudge Joakim decides whether to act on, not a hard stop. Decided 2026-07-19 after wrap-up itself had grown open-ended enough that ending a session took about as long as the work that preceded it (see [documentation/bugs/claude-bugs/under_process/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md](../bugs/claude-bugs/under_process/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md)).

## Post-commit hook (`doc_metrics`/`commit_cost` logging + push, mechanically enforced)

Added 2026-08-04, after `.githooks/pre-commit`'s coverage gate (above) had to
bounce three separate commits in one session because logging kept happening
*after* the fact, one commit late, instead of right away — the gate worked
(nothing shipped unlogged), but every bounce cost a round trip. `.githooks/
post-commit` now runs `tools/doc_metrics/log.py` and `tools/commit_cost/log.py`
right after every commit, and if either produced a new row, auto-commits the
ledger update with the usual `"Log doc metrics and commit cost for the
previous commit"` message — never mixed into the commit that triggered it,
always its own separate commit.

A commit can't carry a ledger row about its own not-yet-computed hash — the
hash is computed *from* the tree, so the tree can't already contain it (see
[DOC_METRICS.md](DOC_METRICS.md)'s "One-commit lag" section) — so the
auto-log commit this hook creates is itself always exactly one commit behind,
by construction, not a bug. The hook recognizes its own commit message and
skips straight past the logging step on that recursive run, so this converges
in exactly one extra commit, never loops.

The hook then pushes the current branch — `git push -u origin <branch>` if
it isn't tracking a remote yet (a brand-new branch's first commit), plain
`git push` otherwise. This runs unconditionally, after every commit, not just
the auto-log one: per Joakim (2026-08-04), commit authorization already
covers pushing and publishing a branch — there is no scenario where he'd
authorize writing local history but not syncing it to the remote he already
granted access to, so this isn't a separate judgment call to make each time.

Tested end-to-end in an isolated temp repo (`.githooks/test_post_commit.sh`)
against a local bare "origin" and stub logging scripts — confirms exactly one
auto-log commit per real commit (no recursion), and that both the first
(branch-publishing) push and subsequent pushes actually land on the remote.
