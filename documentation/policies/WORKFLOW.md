# Workflow

How work happens in this repo, session to session — the operational half of [CLAUDE.md](../../CLAUDE.md)'s working agreement. Hard constraints (what's off-limits) live in [POLICY.md](POLICY.md) instead; nothing here overrides that file.

## Self-sufficiency

This repo is fully self-sufficient — no external memory required. A human developer, or a fresh AI session with zero prior context, must be able to pick this project up entirely from what's checked in here. Decision history, status, future plans, and reusable lessons belong in this repo (CLAUDE.md, POLICY.md, `documentation/changelog/`, the relevant README/TODO per topic) — never only in a private/local AI memory store.

## Ask or search

If a fact is unknown or uncertain (a library's current API/version, a legal/compliance detail, a business rule, anything project-specific not already stated) stop and either ask directly or run a real web search. Never present an assumption or a plausible-sounding guess as fact.

## Testing

Write a failing test before the implementation, every time, confirm it actually fails for the expected reason, then implement — no exceptions for "small" or "obvious" code. Run the fast in-process `app/tests` before every commit, even a docs-only one; for a doc-only commit, skip re-running it if it already ran clean earlier in the same session against the same code. Also run the container-based `server/tests` suite before every commit that touches `server/`/`app/` code. **Why:** decided 2026-07-16 — see `documentation/bugs/claude-bugs/fixed/2026-07-19-skipped-tdd-for-a-small-helper-reasoning-it-wouldn-t-matter.md`. **Partly self-enforcing**: `.githooks/pre-commit` now runs `app/tests` automatically before every commit (added after a third recurrence of skipping it — see `documentation/bugs/claude-bugs/fixed/2026-07-26-skipped-the-mandatory-app-tests-run-before-four-earlier-commits-this-session.md`), but the discipline above still applies in full — the hook is a backstop, not a replacement.

## Dependency freshness

Check for the newest dependency versions before every numbered TODO step (0.1, 0.2, 1.3, etc.), not only when a CVE prompts it. If newer is available, update as part of that step rather than starting on a stale pin. If the update breaks a test, fixing the break is the priority — the step isn't done until the suite is green on the current version. Decided 2026-07-16.

**Automated complement, added 2026-08-07**: the manual per-step check above doesn't run between sessions. GitHub Dependabot is now enabled on this repo (`.github/dependabot.yml`, covering every `pip`/`uv`/`docker` manifest — root, `server/`, `detector/`) — vulnerability alerts + automated security-fix PRs are both on, checked weekly. Notify-only by design, matching this project's "vendor deliberately, don't auto-pull" convention (DETECTORS.md's model-vendoring rule): Dependabot opens a PR or files an alert, a human still reviews and merges, nothing auto-applies to a running system. Runs entirely on GitHub's own infrastructure, independent of whether the `.10` home server or this workstation are up — the deciding factor when this was chosen over a self-hosted cron script. Delivery is email, via each GitHub account's own notification settings (Settings → Notifications → the Dependabot-alerts/security-updates toggles) — not something this repo's config can force on Joakim's behalf; worth him confirming those are checked. Scope is this repo's own dependencies only (Python packages, Docker base images) — the `.10` server's host OS packages are a separate, not-yet-addressed surface, explicitly out of scope for this pass.

## Traceable completion claims and follow-ups

Never claim an action was taken ("logged," "fixed," "ran," "verified," etc.) without checking the corresponding tool call actually ran this turn — don't infer it from intent or from having described the plan. **Why:** this repo is the durable record; see `documentation/bugs/claude-bugs/fixed/2026-07-18-claimed-a-doc-edit-was-made-when-it-wasn-t.md`. Separately: a promised follow-up ("I'll come back to this," "let me get back to you on X") gets a `TodoWrite` item in that same turn, not just a sentence — a promise that only exists as text is invisible to any later self-check. See `documentation/bugs/claude-bugs/fixed/2026-07-18-promised-a-follow-up-mid-conversation-without-tracking-it-as-a-todo.md`.

## Lean, exact, and compact

No filler, no restating what's already documented elsewhere, no speculative abstraction for hypothetical future needs. Documentation should be thorough but slim — sectioned, skimmable, no duplication between files. Cross-references must terminate in real content, not another pointer back (a circular reference silently loses the information both files were supposed to preserve — caught once in README.md ↔ HARDWARE.md; check for it on every new "see X" link). For a full-repo pass applying this at scale, see [CLEANING.md](../tooling/CLEANING.md) (on-demand only, not a per-session step).

**No hard-wrapping prose to a fixed column width** — one paragraph/list-item/blockquote per line, let the viewer soft-wrap. **Why:** measured against the real corpus 2026-07-19 — hard-wrap cost more characters than it saved and the diff-locality benefit was smaller than assumed; full measurement in `CHANGELOG_ARCHIVE.md`'s 2026-07-19T04:39:12+00:00 entry.

## Changelog, doc-metrics, commit-cost logging

One file per entry in `documentation/changelog/` via `tools/create_changelog_entry/create_changelog_entry.sh "Short title"` — never a shared file or hand-named one. Convention: [documentation/changelog/README.md](../changelog/README.md). Never rewrite or reorder past entries, including the frozen `CHANGELOG_ARCHIVE.md`.

Report the character-count change (before → after) for every documentation edit, in the changelog entry and the session's closing summary — measured via [tools/doc_metrics](../tooling/DOC_METRICS.md), not ad hoc `wc`.

Log the real token/dollar cost of every commit via [tools/commit_cost](../tooling/COMMIT_COST.md)'s `log.py`, commit the resulting `commit_costs.jsonl` update.

## Commit and push discipline

Commit coherent chunks of work as you go, push each one to the current branch's remote right after committing — standing authorization, no need to ask first (changed 2026-07-17). Pushing to `master` and publishing new branches is also autonomous for coherent/bigger changes once a merge into `master` is confirmed (decided 2026-07-27, supersedes the narrower 2026-07-17 scope). Force-push and history rewrites stay hand-over-only.

## Branching and merging

New branch, ask first — before starting non-trivial new development work, ask whether to create a new branch and suggest one. Merging into main needs confirmation every time — once Joakim confirms, the merge can be run directly (the confirmation is the authorization, not a request to hand over the command).

## High-blast-radius work

Human-in-the-loop required — draft the action, hand it over, don't execute it directly:

- **Running the app against the real photo library.** Moves/deletes actual files. Only run against `resources/testpics` (or other disposable fixtures) without asking first.
- **Database schema changes** (`CREATE`/`ALTER`/`DROP` etc.) and anything touching the gitignored credentials in `prototypes/differentiate_pictures/app/local_mysql.py`.
- **Any system-level install, config, or deployment** — see [POLICY.md § Deployment and system access](POLICY.md); hand to Joakim as copyable commands.
- **Force-push, or any history rewrite.** (Plain `git push` — including to `master` and new branches — is autonomous; see above. Merging *into* `master` still needs confirmation.)

Everything else — local edits, running the test suite, committing to the current branch — is fine without asking each time.

## Known, accepted permission popups

Claude Code's own hardcoded floors — no `.claude/settings.json` allow-list can suppress these (confirmed 2026-07-17/19). Attempt directly; Joakim approves the popup live.

- **`docker run`/`rmi`/`volume rm`** always prompts, regardless of `Bash(*)`.
- **Reads outside this repo's own directory tree** always prompt. **Never** add a broad/system-wide path (`/`, `$HOME`) to `permissions.additionalDirectories` to work around this — the popup is the safeguard working correctly.
- **Plain, already-allowlisted git commands intermittently prompt too** — tracked upstream as [claude-code#20449](https://github.com/anthropics/claude-code/issues/20449); nothing to fix here, extend that report instead of re-diagnosing.

## Other standing rules

- **Argue with evidence**: if a proposal has a concrete best-practice or precedent-based counter-argument, raise it and explain the trade-off before implementing as asked.
- **Ask for constraints before high-blast-radius work**, rather than waiting for them to surface mid-task.
- **Copyable text goes in one fenced code block** — never inline prose mixed with bold/headers.
- **End substantive sessions with both a durable record and a chat summary.**
- **Bug/incident files start at investigation-open, not fix-time.** Create the file immediately via `tools/create_bug_report/create_bug_report.sh` and update as findings come in. Decided 2026-07-18. Browse `documentation/bugs/repo/under_process/` directly — no index is kept (tried and removed, drifted repeatedly).
