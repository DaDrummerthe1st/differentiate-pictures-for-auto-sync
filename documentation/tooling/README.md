# tooling/

Documentation for project-wide utilities under `tools/` — not tied to any single topic (`picture-handling/`, `photo-server/`, `distributed-sync/`), so they live here rather than in one of those folders. See [TODO.md](TODO.md) for open work.

| File | What's there |
| --- | --- |
| [DOC_METRICS.md](DOC_METRICS.md) | `tools/doc_metrics/` — tracks documentation char-count growth per commit, tied to a `task` label |
| [COMMIT_COST.md](COMMIT_COST.md) | `tools/commit_cost/` — exact real token/dollar cost per commit, from Claude Code's own session transcripts |
| [CLEANING.md](CLEANING.md) | Full, on-demand documentation audit — goals and methodology, not a per-session check |
| [DOCUMENTATION_CHECKS.md](DOCUMENTATION_CHECKS.md) | `tools/documentation_checks/` — the mechanical subset of a CLEANING.md pass (dead links, topic-folder `TODO.md` presence), scripted so it isn't rewritten ad hoc each time |

## Session wrap-up checklist

Every check an AI session working in this repo is expected to run before calling a session done, collected in one place — some are defined in this project's own [CLAUDE.md](../../CLAUDE.md), some in Joakim's cross-project `~/.claude/CLAUDE.md` (marked "global" below; that file applies to every project he works in, so its wording stays generic there — this table is the project-specific copy for quick reference, not a second source of truth to edit independently).

Each check has a trigger condition. Most only apply when something specific happened this session — run the check if the condition is true, skip it (not "run it and find nothing") if it isn't. Decided 2026-07-19: previously every check ran on every session regardless, which made wrap-up itself take about as long as the work it was closing out.

| Check | Trigger | Source |
| --- | --- | --- |
| `app/tests` (fast, in-process) | before every commit, docs-only or not | local |
| `server/tests` (container-based) | every commit touching `server/`/`app/` code; for a doc-only commit, only if it hasn't already run clean this session against the same code | local |
| Secrets-in-diff scan | before every commit | global |
| `doc_metrics` logging | every commit touching a `*.md` file | local |
| `commit_cost` logging | every commit | local |
| CHANGELOG entry | every meaningful change | local |
| `commit_cost` coverage check (`tools/commit_cost/check_coverage.sh`) | every session close | local |
| Lockfile/manifest consistency | only if a manifest file changed this session | global |
| Docker hygiene (dangling/abandoned images) | only if `docker build`/`compose build` ran this session | global |
| Cross-reference link check | only if a "see X" doc link was touched this session | global |
| Doc-drift check (status lines/TODO/specs vs. code) | only if code or docs changed this session | global |
| Wider sweep (stale dependency versions, dead code, stale TODO/FIXME references, security gaps) | scoped to files touched this session | global |
| Loose ends in the chat (unanswered questions, dropped "I'll get back to you" threads, unresolved TBDs) | every session close | global |
| Stale-TODO glance (items already resolved but still marked open) | every session close | global |
| Forward-effectiveness note (one concrete note on what would make the next session cheaper) | every session close | global |
| Systematic security-discovery pass (`pip-audit`, OWASP ZAP scan — see [PHOTO_SERVER's TODO.md](../photo-server/TODO.md)) | not diff-triggered — audits the live deployed surface, not a change; needs a real recurring schedule once built, not a per-session check | local, not built yet |

**Persistent nudge, not a one-time flag**: once a session shows drift (a second, unrelated concern enters the conversation) or has clearly run long, say so plainly in every subsequent message until the session actually ends — starting as soon as the signal appears, not at a context-limit warning. This is a nudge Joakim decides whether to act on, not a hard stop. Decided 2026-07-19 after wrap-up itself had grown open-ended enough that ending a session took about as long as the work that preceded it (see [documentation/bugs/claude/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md](../bugs/claude/2026-07-18-session-wrap-up-itself-grows-unpredictably-long.md)).
