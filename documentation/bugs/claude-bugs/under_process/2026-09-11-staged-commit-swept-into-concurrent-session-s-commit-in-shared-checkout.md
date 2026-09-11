# Staged commit swept into concurrent session's commit in shared checkout

See [README.md](../README.md) for what belongs here.

## What happened

Asked to persist a deferred item (a paused NAS sync-contract review) as a `mobile/TODO.md` entry,
then commit only that edit. Used `git add -p` to stage just the one hunk I'd written, leaving two
other hunks (a face-recognition status bullet, a runtime-conflict note) that a concurrently-live
peer session had added to the same file, unstaged — correct so far, matches this file's own
"no worktree isolation" rule about being careful in a shared checkout.

The session was then paused (per the user's "need to stop asap") and resumed roughly two days of
in-story time later (system date moved 2026-09-09 -> 2026-09-11 between turns). On resume, I ran
`git commit -m "Document paused NAS sync-contract review..."` directly, without first checking
`git log`/`git status` for what might have happened in the shared checkout during the gap. The
pre-commit hook ran clean (secrets scan clean, ledger coverage OK) and printed no error, but the
command's own tail output was `no changes added to commit (use "git add" and/or "git commit -a")`
— easy to miss since it followed a wall of hook success output that looked like everything worked.

`git log`/`git reflog` afterward showed why: during the pause, the peer session made its own real
commit, `746ef9f "Add changelog entry for mobile backlog checklist and triage glossary term"`. It
shares this same working directory and `.git` index (no worktree), so its commit swept up whatever
was sitting staged at the time — my already-staged `mobile/TODO.md` hunk — into its own commit,
under its own unrelated message. By the time my `git commit` ran, the index had nothing left
staged, so it aborted with no error, just that one easily-missed line. My content is not lost (it's
inside `746ef9f`, which was also already auto-pushed by that session's post-commit hook), but it's
misattributed: a different commit message than intended, bundled with unrelated files, and my own
intended message never used anywhere. Caught before pushing anything further or claiming success,
by manually re-diffing/inspecting `HEAD` rather than trusting the hook's clean output.

## Why it happened

Trusted "the pre-commit hook printed no error" as equivalent to "my commit succeeded with my
intended content," without checking `git log -1 --format=%B` (or the file list) against what was
actually intended, immediately after the commit command returned. In a checkout known to have
other live sessions, a clean hook run only proves the *content that ended up committed* passed the
secrets/ledger checks — it says nothing about whose content that was or under what message, since
staging and committing both operate on a shared index another process can mutate between your own
tool calls (including across a real time gap while the session sits paused).

## What changed

Added a new bullet to `documentation/policies/WORKFLOW.md`'s existing "no isolation between
concurrent Claude Code sessions" rule: after every `git commit` in a shared (non-worktree)
checkout, verify `git log -1 --format=%B` (and, if in doubt, `git show --stat HEAD`) matches the
message and files actually intended *before* reporting success or pushing — don't infer success
from clean pre-commit-hook output alone, and don't skip this check just because no error was
printed. Applies with extra force after any pause/resume, since that's exactly the window a peer
session's own commit can land in.
