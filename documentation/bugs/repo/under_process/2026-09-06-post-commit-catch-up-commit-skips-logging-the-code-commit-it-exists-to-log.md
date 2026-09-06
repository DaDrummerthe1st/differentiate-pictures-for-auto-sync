# post-commit catch-up commit skips logging the code commit it exists to log

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Committing `37cdda2` ("Scrap the Slice 1 Android plan...") succeeded and `.githooks/post-commit`
ran, logged `doc_metrics` for it, found nothing pending for `commit_cost` (correctly deferring
`37cdda2`'s own row by the documented one-commit lag — see
[DOC_METRICS.md](../../../tooling/DOC_METRICS.md)'s "One-commit lag" section), and auto-created the
usual catch-up commit `b7ae3cb` ("Log doc metrics and commit cost for the previous commit") on top.

The very next real commit attempt was then blocked by `.githooks/pre-commit`'s coverage gate:

```
[MISSING] commit_cost: 1 commit(s) with no logged row (run tools/commit_cost/log.py):
  37cdda2e48bacfa38ecb948c34b99b7d3941e705
```

`37cdda2` was never logged. Worked around by running `python3 tools/commit_cost/log.py` by hand
(no flags), which found and logged it immediately.

## Investigation log

1. Read `.githooks/post-commit`: it guards its entire logging block with
   `if ! is_catch_up_title "$(git log -1 --format=%s)"`. When `b7ae3cb` (the catch-up commit
   itself) became `HEAD`, that guard is true (its own title matches), so the hook's *next*
   invocation (triggered by `b7ae3cb`'s own commit, since committing re-triggers the hook)
   skips the whole logging block entirely — it never calls `commit_cost/log.py` again for
   `b7ae3cb`'s own creation.
2. `37cdda2`'s row was supposed to be caught up by exactly that skipped call (per the "one-commit
   lag" design: a commit's row is written by the *next* commit's post-commit run). Because that
   next run belonged to the catch-up commit itself, and catch-up commits are deliberately exempted
   from re-running the logging step (to avoid infinite recursion), the row for `37cdda2` fell
   through — nobody ever called `log.py` for it.
3. Confirmed this isn't a one-off: it's a structural gap any time a catch-up commit's own creation
   is the "next commit" that was supposed to close the previous lag — which is *every* time,
   since the catch-up commit is always the very next commit after the one it's catching up.

## Leading theory (unconfirmed)

The recursive `git commit` inside `post-commit` re-triggers the hook for the catch-up commit
itself, and the `is_catch_up_title` guard - added to stop that recursion from running forever -
also accidentally suppresses the one logging call that was supposed to close the lag for the
*previous*, real commit. The guard needs to distinguish "don't log costs for me, the catch-up
commit" from "don't bother catching up the commit before me either" - right now it conflates both.

## Next session should start with

Fix `.githooks/post-commit` so the catch-up commit still logs `commit_cost` for the commit it's
catching up (its parent), even though it skips logging for itself. Likely fix: run
`commit_cost/log.py` (no `--exclude-current-head`) *before* the `is_catch_up_title` check bails
out, or restructure so the check only guards the "create another catch-up commit" step, not the
"log the parent" step. Verify by making two commits in a row without manually running
`tools/commit_cost/log.py` in between and confirming `pre-commit`'s coverage gate stays green.
