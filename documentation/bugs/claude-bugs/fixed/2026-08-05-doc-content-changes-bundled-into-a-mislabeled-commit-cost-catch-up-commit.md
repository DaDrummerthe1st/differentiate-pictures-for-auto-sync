# Doc-content changes bundled into a mislabeled commit_cost catch-up commit

See [README.md](../README.md) for what belongs here.

## What happened

Mid-session, `git add documentation/GLOSSARY.md documentation/curation/DETECTORS.md
documentation/curation/RESEARCH_QUEUE.md` was run to stage a real documentation commit (closing six
`RESEARCH_QUEUE.md` items). The commit was blocked by the pre-commit hook's `commit_cost`/`doc_metrics`
coverage check (an earlier commit was missing a logged row). Fixing that meant running
`tools/commit_cost/log.py`, then `git add tools/commit_cost/commit_costs.jsonl && git commit -m
"Log doc metrics and commit cost for the previous commit"` — but `git add` only *adds to* the index,
it doesn't replace it, so the three already-staged documentation files rode along into that commit
too. The result: commit `17f12bf` is titled "Log doc metrics and commit cost for the previous commit"
but its actual diff is 98 insertions/30 deletions across `GLOSSARY.md`, `DETECTORS.md`,
`RESEARCH_QUEUE.md`, plus the 2-line `commit_costs.jsonl` catch-up — the real content commit never
happened as its own commit. Both this catch-up commit and the next one (`7384c91`) were pushed
automatically by the post-commit hook before the mislabeling was noticed. No content was lost — every
intended change is present in the repo, correctly — but the commit history now misattributes a
substantial, meaningfully-titled change to a housekeeping commit message, which breaks `git log`/
`git blame` as a reliable record of *why* a change happened (this project's own stated reason for
per-entry-dated files, changelogs, etc.). Rewriting history to fix it would mean force-pushing
already-pushed commits, which needs Joakim's explicit go-ahead per the git safety protocol — not
attempted unilaterally; filed here instead so the record accurately shows the mistake did happen,
per this project's own bug-tracker rule, rather than silently leaving it unremarked in the log.

## Why it happened

The catch-up-commit pattern (stage the ledger file, commit with a fixed generic message) assumes the
index is clean of anything else at that moment. Nothing in `COMMIT_COST.md`/`DOC_METRICS.md` or the
wrap-up checklist says to check `git status`/`git diff --cached --stat` immediately before running a
catch-up commit specifically — the assumption "the index only has the ledger file in it" was never
verified, and in this session it was false because a real commit's `git add` was already sitting
staged, blocked by the very hook the catch-up commit exists to satisfy. This is a real structural trap
in the pattern: the coverage check that blocks a commit for missing ledger rows is discovered
*after* staging the real change, and the fix for it (`git add` the ledger file) doesn't know or care
what's already staged.

## What changed

Added a line to [documentation/tooling/README.md](../../../tooling/README.md)'s catch-up-commit
guidance: before running a `commit_cost`/`doc_metrics` catch-up commit (staging only the ledger
file), first run `git status --short` and confirm nothing else is staged — if something else is
staged, unstage it (`git restore --staged <path>`) before the catch-up commit, then re-stage and
commit it separately afterward. This makes the "catch-up commits should only ever contain the ledger
file" assumption something actually checked, not just assumed true.
