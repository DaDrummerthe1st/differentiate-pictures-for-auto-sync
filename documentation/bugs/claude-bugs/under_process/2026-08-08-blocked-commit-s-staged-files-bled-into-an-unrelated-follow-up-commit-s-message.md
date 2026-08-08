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
committed this time. **Correction after first drafting this report**: a rule for exactly this already
existed - `documentation/tooling/README.md`'s pre-commit hook section, added after an earlier,
different incident: *"If this gate blocks a commit that already has files staged... run `git status
--short` before staging and committing the ledger catch-up file, and confirm nothing else is staged.
If something else is staged, `git restore --staged <path>` it first..."* This session simply didn't
check that doc before retrying the commit - so the real lapse is narrower than first described: not
"no rule existed," but "an existing, already-battle-tested rule wasn't consulted in the moment it
applied."

## What changed

No CLAUDE.md/doc change made this time - the rule was already correctly written down
(`documentation/tooling/README.md`, quoted above); the gap was following it, not documenting it.
Second occurrence of the pre-commit-gate-plus-stale-stage-set pattern (see that same doc's note that
this section already came from "the incident that found this"), which suggests the doc note alone
isn't consistently surfacing in the moment - worth flagging to Joakim as a candidate for the
pre-commit hook itself printing that exact `git status --short` reminder in its blocked-commit output,
rather than relying on the AI session to recall the doc unprompted. Not implemented here (would need
Joakim's sign-off on hook behavior) - flagged as the concrete next step instead of invented as done.
This session's own remaining commits were made correctly (checked `git status --staged --stat` before
each retry) once this was noticed.
