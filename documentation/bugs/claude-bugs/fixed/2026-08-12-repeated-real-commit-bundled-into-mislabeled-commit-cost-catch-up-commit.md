# Repeated: real commit bundled into mislabeled commit_cost catch-up commit

See [README.md](../README.md) for what belongs here.

## What happened

Same lapse as [2026-08-05-doc-content-changes-bundled-into-a-mislabeled-commit-cost-catch-up-
commit.md](../fixed/2026-08-05-doc-content-changes-bundled-into-a-mislabeled-commit-cost-catch-up-commit.md),
despite the fix that entry produced already being in place. A real commit (the upload-completion-
feedback fix, its regression test, GLOSSARY.md, TODO.md, the new changelog entry, and the new plan
file) was `git add`-ed and committed, blocked by the pre-commit `commit_cost` coverage gate (an
earlier commit, `8ff7581`, had no logged row). Ran `tools/commit_cost/log.py --exclude-current-head`
to catch it up, then `git add tools/commit_cost/commit_costs.jsonl && git commit -m "Log commit cost
for the previous commit"` — without first running `git status --short` to confirm the index held
only the ledger file, exactly the check the prior incident's fix added to
[documentation/tooling/README.md](../../../tooling/README.md). The already-staged real files rode
along. Result: commit `fa84557`, titled "Log commit cost for the previous commit", actually contains
the real feature diff (63 insertions, 22 deletions across 7 files) plus the 1-line ledger catch-up.
Both it and the following auto-generated doc_metrics/commit_cost commit (`3356b43`) were pushed by
the post-commit hook before the mislabeling was noticed. No content lost, correctly present in the
repo; history misattributes it. Not rewritten unilaterally — force-pushing already-pushed commits
needs Joakim's explicit go-ahead per the git safety protocol; flagged to him in chat instead.

## Why it happened

The documented check exists and was read as part of this same session's context, but wasn't actually
run in the moment — knowing the rule and executing it under a multi-step tool-call sequence are not
the same thing, and nothing forces the check the way a hook does. The 2026-08-05 fix added guidance
to a doc, which is necessary but wasn't sufficient here: it depends on the AI session itself
remembering to look before every catch-up commit.

## What changed

Turned the doc-only guidance into a mechanical check: `tools/commit_cost/log.py` now refuses to run
its catch-up commit workflow — well, it doesn't commit anything itself, so instead the fix is in
[documentation/tooling/README.md](../../../tooling/README.md): replaced the prose instruction with
a copy-pasteable one-liner (`git status --short --porcelain | grep -qv commit_costs.jsonl && echo
"STOP: something else is staged" || echo "clean, safe to commit"`) directly in the catch-up recipe,
so the check is a command to run, not a rule to remember.
