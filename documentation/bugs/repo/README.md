# bugs/repo/

Bugs in the project's own codebase — not AI-session process lapses, see [../claude-bugs/](../claude-bugs/README.md) for those.

**Hard rule: every bug is its own file, named `<date>-<short-slug>.md` — never a bullet added to a shared list.** This applies even to a one-line bug, not just multi-session investigations — the file is where the *process* (what was checked, what was ruled out, in order) lives as it's learned, not just the conclusion — see [under_process/2026-07-17-thumbnail-oom-under-load.md](under_process/2026-07-17-thumbnail-oom-under-load.md) for the shape to follow.

Use `tools/create_bug_report/create_bug_report.sh "Short bug title"` to create one with a consistent name and the right starter template in [under_process/](under_process/) — don't hand-name these.

**On move to fixed**: not mitigated, not "probably fine now," genuinely confirmed resolved. Use `tools/create_bug_report/mark_solved.sh <filename>` to move it into [fixed/](fixed/), renamed to append `-SOLVED` before `.md` (e.g. `2026-07-17-thumbnail-oom-under-load.md` -> `2026-07-17-thumbnail-oom-under-load-SOLVED.md`), keeping the original `<date>-<slug>` prefix so it still sorts and greps the same way. Moved rather than deleted so the investigation trail (what was tried, what worked) stays available for a similar bug later.

**Also on move**: append a `## Security analysis` section covering what the fix changed, what attack surface or data handling it does or doesn't affect, and any residual risk — before calling the bug closed, not only if Joakim asks "is this safe?" afterward (global CLAUDE.md's mirrored rule, decided 2026-07-21). If that analysis surfaces a real, non-theoretical risk, raise it to Joakim directly in the conversation in addition to writing it here. See [fixed/2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions-SOLVED.md](fixed/2026-07-18-redis-has-no-persistent-volume-every-restart-wipes-active-sessions-SOLVED.md) for the worked example (the residual risk it found — an AOF-corruption startup failure with no health check — is tracked as a follow-up in [photo-server/TODO.md](../../photo-server/TODO.md)).
