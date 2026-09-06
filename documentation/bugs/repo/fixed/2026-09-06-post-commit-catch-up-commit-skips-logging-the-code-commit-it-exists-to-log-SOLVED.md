# post-commit catch-up commit skips logging the code commit it exists to log

Status: **fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

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

**Recurred a second time in the same session**, on the very next real commit after that — same
symptom, same workaround — confirming this wasn't a one-off but a structural, every-single-time gap.

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
   Reproduced a second time in the same session (see Symptom above) before a fix was written,
   confirming the "every time" prediction rather than assuming it.
4. Found a closely related, previously "fixed" bug on the same mechanism:
   `documentation/bugs/repo/fixed/2026-09-05-post-commit-hook-s-self-recursion-guard-only-recognizes-one-of-the-three-commit-msg-allowed-catch-up-titles-SOLVED.md`
   — a *different* gap in the same title-matching recursion guard, patched one day before this bug
   was found. Two distinct bugs in the same guard within 24 hours was read as a signal that the
   title-matching auto-commit design itself was fragile, not just missing one more edge case to
   patch — see "Fix" below.

## Fix

Replaced the whole mechanism rather than patching the guard again. `.githooks/pre-commit` now runs
`tools/doc_metrics/log.py` and `tools/commit_cost/log.py` unconditionally (plain, no
`--exclude-current-head`) before its coverage check, and `git add`s any resulting jsonl changes into
the commit already being made. At pre-commit time `HEAD` is still the *previous* commit — one whose
own `git commit` tool call already completed in an earlier turn, so its transcript is fully written,
which is exactly why the previous design's transcript-in-flight problem (the reason
`--exclude-current-head` existed) doesn't apply here. Both `log.py` scripts already dedupe by
`commit_hash`, so calling them on every commit is safe even when nothing's missing.

`.githooks/post-commit` no longer logs anything or creates any commit — it only pushes. With no
auto-generated commit ever created, there is no recursion to guard against and no commit-message
convention to enforce, so `.githooks/commit-msg` and `.githooks/catch_up_titles.sh` (the mechanism
both this bug and the 2026-09-05 one lived in) were deleted entirely rather than patched a third
time. Full writeup: `documentation/tooling/README.md`'s "Self-healing doc_metrics/commit_cost
logging" section, `documentation/tooling/DOC_METRICS.md`'s "One-commit lag" section,
`documentation/tooling/COMMIT_COST.md`'s edge-cases list.

## Verified

`.githooks/test_commit_hooks.sh` (replacing `test_post_commit.sh`, which tested the retired design)
runs the new pre-commit + post-commit pair end-to-end in an isolated temp repo against a local bare
"origin" and stub logging scripts: six real commits in a row, each one's pre-commit run folding the
*previous* commit's ledger rows straight into itself, asserting after every commit that (a) no extra
commit was ever created, (b) the expected rows exist in the commit's own tree, (c) `commit_cost`
stub was never invoked with `--exclude-current-head`, and (d) both the first (branch-publishing) push
and every push after land correctly on the remote. All assertions passed. Also ran manually against
the real repo for two more commits after the fix (this bug report's own filing and one code fix) with
zero manual intervention and a clean coverage check both times.

## Security analysis

Change is confined to `.githooks/pre-commit`, `.githooks/post-commit`, and deleting
`.githooks/commit-msg`/`.githooks/catch_up_titles.sh` — no user input, no network calls, no
credentials, no change to what data is read or written (still only
`tools/commit_cost/commit_costs.jsonl` and `tools/doc_metrics/metrics.jsonl`, both already
git-tracked, non-secret ledgers). The only behavior change is *when* and *how* those two files get
updated and committed; removing the auto-generated commit and its title-matching guard shrinks the
hook's effective surface area rather than growing it. No new attack surface, no residual risk
identified.
