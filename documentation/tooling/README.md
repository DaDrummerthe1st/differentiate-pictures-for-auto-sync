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
| Product code test suite | before every commit touching live product code, docs-only or not | local. **Real tests exist as of 2026-09-06** — `android/app/src/test/` (Robolectric, `PhotoAdapterTest`/`FullscreenPhotoActivityTest`), run via `./gradlew testDebugUnitTest` (needs `JAVA_HOME=~/.jdks/jbr-21.0.11`, not this machine's Android-Studio-bundled JBR 25 — see [mobile/README.md](../mobile/README.md)). `.githooks/pre-commit` still runs no test-suite gate for `android/` — wiring `gradlew testDebugUnitTest` into it (with the right `JAVA_HOME`) is still open, deliberately not rushed into this session's already-large diff |
| Secrets-in-diff scan | before every commit | local, mechanically enforced by `.githooks/pre-commit` via `tools/secrets_scan/` (see [SECRETS_SCAN.md](SECRETS_SCAN.md)) — see below |
| `test_results` logging | after each `app/tests`/`server/tests` run, if tracking that run's trend is useful | local, see [TEST_RESULTS.md](TEST_RESULTS.md) |
| `doc_metrics` logging | every commit touching a `*.md` file | local, mechanically enforced by `.githooks/pre-commit` — see below |
| `commit_cost` logging | every commit | local, mechanically enforced by `.githooks/pre-commit` — see below |
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

## Pre-commit hook (secrets scan + self-healing ledger logging + coverage check, mechanically enforced)

Added 2026-07-27 after an AI session committed twice in a row without running
`app/tests` first, despite the rule above already saying to
(see `documentation/bugs/claude-bugs/`) — wording alone wasn't enough, so this
makes the fast-suite-before-commit rule self-enforcing instead of
memory-dependent. `.githooks/pre-commit` runs `app/tests` and blocks the commit
on failure; it only reminds (doesn't block) about `server/tests` when a commit
touches `server/`/`app/`, since that suite is container-based, slower, and the
rule's "skip if already run clean this session" judgement call isn't
mechanically checkable.

**2026-09-05**: the test-suite gate described above is currently disabled — there is no live
product test suite to run (`modules/`/`contacts/` were archived to `previous-work/` in the
native-app pivot). Only the secrets scan and ledger-coverage gates below are currently active.
Re-add a gate here once real code exists again.

The same hook then runs `tools/secrets_scan/run.py` (added 2026-08-03, per
[TODO.md](TODO.md)'s 2026-07-28 item) and blocks the commit on any finding —
see [SECRETS_SCAN.md](SECRETS_SCAN.md) for what it checks and why a
generic "password=" heuristic was deliberately left out.

Before that, the hook runs `tools/doc_metrics/log.py` and `tools/commit_cost/log.py`
unconditionally, self-healing any gap left by the *previous* commit and folding the result straight
into the commit already being made (`git add`, no separate commit) — see the "Self-healing
doc_metrics/commit_cost logging" section below. Finally it runs
`tools/wrapup_checklist/run.py --coverage-only`, which should then always find both ledgers already
clean; it stays as a safety net, not the primary mechanism, and blocks the commit if it ever does
find a gap (a sign the self-heal step itself failed, not something to work around by hand) —
retiring the two standalone `check_coverage.sh` scripts that used to only run when a session
remembered to at wrap-up (see [WRAPUP_CHECKLIST.md](WRAPUP_CHECKLIST.md)'s "Scaling" and
"Enforcement" sections for why this closes that gap and how it stays fast as the repo grows).

## Self-healing doc_metrics/commit_cost logging (mechanically enforced)

Added 2026-09-06, replacing an earlier design (2026-08-04–2026-09-06) where `.githooks/post-commit`
ran the logging tools right after every commit and auto-committed the result as a separate
"catch-up" commit. That design had a structural gap: its own recursion guard (needed to stop the
auto-commit from re-triggering itself forever) also skipped the one logging call that was supposed
to close the gap for the *real* commit before it — every catch-up commit silently reintroduced the
exact gap it existed to close, surfacing later as a blocked commit. Root-caused and retired — see
`documentation/bugs/repo/fixed/2026-09-06-post-commit-catch-up-commit-skips-logging-the-code-commit-it-exists-to-log-SOLVED.md`.

The fix: move the logging into `.githooks/pre-commit`, which runs *before* the commit-to-be exists,
so `HEAD` at that point is still the previous commit — one whose own `git commit` tool call already
completed in an earlier turn, so its transcript is fully written (not the "still in-flight" case
`--exclude-current-head` used to guard against). `python3 tools/doc_metrics/log.py` and
`python3 tools/commit_cost/log.py` run plain, unconditionally, on every commit attempt; both are
idempotent (dedupe by `commit_hash`), so there's no harm in calling them when there's nothing new to
log. Any resulting jsonl changes are `git add`ed into the commit already in progress. No separate
commit is ever created, so there's no recursion to guard against and no commit-message convention to
enforce — `.githooks/commit-msg` and `.githooks/catch_up_titles.sh` (the mechanism that used to
police the three recognized catch-up-commit titles) were deleted as dead weight along with it.

Verified end-to-end in an isolated temp repo (`.githooks/test_commit_hooks.sh`) against a local bare
"origin" and stub logging scripts: six commits in a row, each folding the previous commit's ledger
rows straight into itself, zero extra commits ever created, coverage clean throughout, every push
landing correctly (both the first, branch-publishing push and every one after).

**Not active by default** — git doesn't read hooks from a repo-tracked
directory on its own. One-time setup, per clone:

```
git config core.hooksPath .githooks
```

This changes local git config, so it's a command to run yourself, not
something an AI session runs on your behalf (see CLAUDE.md's git safety
protocol) — hand it over once per clone.

**Persistent nudge, not a one-time flag**: once a session shows drift (a second, unrelated concern enters the conversation) or has clearly run long, say so plainly in every subsequent message until the session actually ends — starting as soon as the signal appears, not at a context-limit warning. This is a nudge Joakim decides whether to act on, not a hard stop. Decided 2026-07-19 after wrap-up itself had grown open-ended enough that ending a session took about as long as the work that preceded it (see [documentation/bugs/claude-bugs/under_process/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md](../bugs/claude-bugs/under_process/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md)).

## Post-commit hook (push, mechanically enforced)

Added 2026-08-04. Until 2026-09-06 this hook also ran the doc_metrics/commit_cost logging (see
"Self-healing doc_metrics/commit_cost logging" above for why that moved to `.githooks/pre-commit`
instead) — today its only job is pushing the branch just committed to: `git push -u origin <branch>`
if it isn't tracking a remote yet (a brand-new branch's first commit), plain `git push` otherwise.
Runs unconditionally, after every commit: per Joakim (2026-08-04), commit authorization already
covers pushing and publishing a branch — there is no scenario where he'd authorize writing local
history but not syncing it to the remote he already granted access to, so this isn't a separate
judgment call to make each time.

Tested end-to-end, together with `.githooks/pre-commit`, in an isolated temp repo
(`.githooks/test_commit_hooks.sh`) against a local bare "origin" and stub logging scripts — see the
"Self-healing doc_metrics/commit_cost logging" section above for what it confirms.
