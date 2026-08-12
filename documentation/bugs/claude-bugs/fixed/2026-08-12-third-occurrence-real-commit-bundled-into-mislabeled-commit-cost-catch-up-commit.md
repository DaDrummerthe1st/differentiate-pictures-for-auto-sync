# Third occurrence: real commit bundled into mislabeled commit_cost catch-up commit

See [README.md](../README.md) for what belongs here.

## What happened

Same lapse as [2026-08-05-doc-content-changes-bundled-into-a-mislabeled-commit-cost-catch-up-
commit.md](../fixed/2026-08-05-doc-content-changes-bundled-into-a-mislabeled-commit-cost-catch-up-commit.md)
and [2026-08-12-repeated-real-commit-bundled-into-mislabeled-commit-cost-catch-up-commit.md](../fixed/2026-08-12-repeated-real-commit-bundled-into-mislabeled-commit-cost-catch-up-commit.md),
despite both fixes already being in place — the second of which specifically added a
copy-pasteable `git status --short` check to the catch-up recipe. A real commit (`app/auth.py`,
`app/main.py`, `app/benchmark_detector.py`, six test files, one deleted test file, one new
changelog entry — the `deep-singing-firefly.md` username-scoping increment) was staged and
committed, blocked by the pre-commit `commit_cost` coverage gate (an earlier commit, `66f37ad`,
had no logged row). Ran `tools/commit_cost/log.py` to catch it up, then `git add
tools/commit_cost/commit_costs.jsonl && git commit -m "Log doc metrics and commit cost for the
previous commit"` — again without running the documented `git status --short` check first. The
already-staged real files rode along again. Result: commit `e85805e`, titled "Log doc metrics and
commit cost for the previous commit", actually contains the full real diff (225 insertions, 382
deletions across 13 files) plus the 1-line ledger catch-up. Already pushed by the time this was
noticed (the post-commit hook pushes immediately). No content lost, correctly present in the repo;
history misattributes it. Not rewritten unilaterally — force-pushing an already-pushed commit needs
Joakim's explicit go-ahead per the git safety protocol; flagged to him in chat instead.

## Why it happened

Two compounding causes, not one:

1. The same root cause as both prior entries: prose guidance — even a literal copy-pasteable
   command in a recipe doc — depends on an AI session choosing to run it at the right moment in a
   multi-step tool-call sequence, and that choice doesn't reliably survive contact with "the commit
   got blocked, let me just fix the blocker and retry."
2. **Newly discovered while investigating this occurrence: the documented check itself was silently
   broken in this exact execution environment.** The 2026-08-12 predecessor fix's recipe was `git
   status --short --porcelain | grep -qv 'commit_costs.jsonl\|metrics.jsonl' && echo STOP || echo
   "clean, safe to commit"`. In Claude Code's Bash tool specifically, `grep` resolves to a shell
   *function* (visible via `type grep`) that execs `ugrep` with extra flags - and that wrapper's
   `-q` combined with `-v` returns the wrong exit code: verified directly with 3 non-matching lines
   and 1 matching line in the input, `grep -qv pattern` exits 1 (as if nothing matched) even though
   `grep -v pattern` alone (no `-q`) correctly prints the 3 non-matching lines. So the one-liner
   printed "clean, safe to commit" even with real files staged, in every session running it via this
   tool - meaning even a session that dutifully ran the check exactly as written would have been
   told to proceed. Two rounds of "write it down more clearly" couldn't have closed this gap even
   with perfect compliance, because the tool itself lied.

## What changed

Added `.githooks/commit-msg` (plus `.githooks/test_commit_msg.sh`, an isolated-repo integration
test mirroring `test_post_commit.sh`'s pattern): a mechanical, unskippable gate that inspects the
actual commit message against the three known catch-up titles ("Log doc metrics and commit cost for
the previous commit", "Log commit cost for the previous commit", "Log doc metrics for the previous
commit") and, if matched, refuses the commit unless the staged diff is *exclusively*
`tools/commit_cost/commit_costs.jsonl` and/or `tools/doc_metrics/metrics.jsonl`. Unlike the
2026-08-12 fix (a doc-recipe check an AI session has to remember to run), this can't be skipped by
forgetting, and it's immune to the `grep -qv` bug above too - the hook checks staged-file content
directly (`grep -vE "$ALLOWED_REGEX"`, no `-q`, judged by whether its output is non-empty) rather
than trusting any grep implementation's exit-code semantics for an inverted+quiet combination.
`documentation/tooling/README.md`'s catch-up recipe section was also rewritten to point at the hook
instead of the broken one-liner. Both prior fixed-folder entries' lesson ("doc guidance isn't
enough here") is now actually acted on rather than repeated a third time in the fix section too.
