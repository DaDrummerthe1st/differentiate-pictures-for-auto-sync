# Blocked commit's staged files bled into an unrelated follow-up commit's message

See [README.md](../README.md) for what belongs here.

## What happened

Staged all of this session's Phase 3 (face detection) files with `git add` and ran `git commit`. The
pre-commit hook blocked it: a prior commit (`a2787cd`) had no logged `commit_cost` row. Ran
`tools/commit_cost/log.py --exclude-current-head` to catch up, then `git add
tools/commit_cost/commit_costs.jsonl` and `git commit -m "Log commit cost for the previous commit"` -
intending that second commit to contain *only* the catch-up log row, matching this repo's own
observed pattern of a small standalone "Log doc metrics and commit cost for the previous commit"
commit. Instead the resulting commit (`b0a02e8`) contains all 12 files - the full Phase 3 face-
detection work plus the log row - because the earlier blocked `git commit` never unstaged anything;
the Phase 3 files were still staged from before, and the second `git add` only added one more file on
top of that already-staged set. Content is fully correct (same files, same diff that would have been
committed under the intended message); only the commit message is wrong for what it actually contains.
Both commits were already pushed (the repo's post-commit hook auto-pushes) before this was noticed,
so fixing the message would need an amend + force-push of already-shared history - held off per the
global CLAUDE.md's "never force-push without explicit confirmation" default; flagged to Joakim instead
of unilaterally rewriting it.

## Why it happened

A blocked `git commit` (non-zero exit from a failing hook) does not unstage the index - the files
stay staged exactly as before. This session treated "the commit was blocked" as "nothing happened"
and moved on to stage one more file for what was intended to be a small, separate follow-up commit,
without first checking `git status`/`git diff --staged` to confirm what was actually about to be
committed this time. The mistake was in not re-verifying staged content before a second `git commit`
call in the same sequence, not in the tooling itself.

## What changed

No rule existed yet for "what to check before retrying a commit after a hook-blocked one." Going
forward (own working practice, not yet promoted into a CLAUDE.md file since that requires Joakim's
sign-off): after any blocked commit, run `git status`/`git diff --staged --stat` immediately before
the next `git commit` call in the same sequence, rather than assuming a freshly-staged single file is
the only thing about to be committed - the index does not reset itself just because a hook rejected
the previous attempt.
