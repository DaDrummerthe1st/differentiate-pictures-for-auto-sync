# File bug report on concurrent-session working-directory confusion

While committing the `quality.py` rename, another concurrently-running Claude Code session switched the shared working directory's branch and merged `master` into `test_production1` mid-chase, making the `commit_cost` pre-commit hook's catch-up chain look like an unbounded loop (5+ rounds, real session cost incurred). No work was lost - `ebdffa2` (the rename commit) landed on both `master` and `test_production1` - but the confusion and its likely cause (no isolation between concurrent sessions sharing one working tree) is filed as `repo/under_process/2026-09-04-concurrent-sessions-...md` for a future session to investigate and, if confirmed, propose a CLAUDE.md/WORKFLOW.md convention for.

- **Doc size**: `documentation/bugs/repo/under_process/2026-09-04-concurrent-sessions-sharing-one-working-directory-caused-branch-switch-confusion-and-a-false-infinite-commit-cost-catch-up-chain.md` +4215 chars (new file).
