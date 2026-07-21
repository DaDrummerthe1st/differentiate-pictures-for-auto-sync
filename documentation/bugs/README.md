# bugs/

Two independent trackers, split by what kind of bug they hold — each with its own `README.md` and `TODO.md`:

- [claude-bugs/](claude-bugs/README.md) — the AI session's own process lapses (a routine that should have run per an existing rule and didn't, a claim made without checking it first). Not application bugs.
- [repo/](repo/README.md) — bugs in the project's own codebase.

Both split the same way: `fixed/` for resolved entries, `under_process/` for open ones. One file per bug in whichever subfolder matches its current status; `git mv` it across when status changes rather than duplicating or rewriting history.

Use `tools/create_bug_report/create_bug_report.sh "Short bug title"` (add `--claude` for a claude-bugs entry) to create one with a consistent name and starter template — don't hand-name these. Once genuinely resolved (not just mitigated), move it with `tools/create_bug_report/mark_solved.sh <filename>` (add `--claude` for a claude-bugs entry) into the matching `fixed/` folder.

No index is kept at this level or below — see each subfolder's own `TODO.md` for why, and browse `fixed/`/`under_process/` directly for what's open.
