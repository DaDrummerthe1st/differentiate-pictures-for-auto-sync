# post-commit hook's self-recursion guard only recognizes one of the three commit-msg-allowed catch-up titles

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

An AI session hand-committed a `commit_cost` catch-up (only `tools/commit_cost/commit_costs.jsonl` staged) titled `Log commit cost for the previous commit` — a title `.githooks/commit-msg` explicitly allows (its `case` statement lists three valid catch-up titles: `"Log doc metrics and commit cost for the previous commit"`, `"Log commit cost for the previous commit"`, `"Log doc metrics for the previous commit"`).

That commit's own `post-commit` hook then ran normally (its `HEAD` message didn't match its `LOG_COMMIT_MSG` constant, which is hardcoded to only the first of those three strings), found the ledger diff, and auto-created a *second* commit titled `Log doc metrics and commit cost for the previous commit` to hold it. That second commit's own `post-commit` run recognized itself (message matches `LOG_COMMIT_MSG`) and stopped — but by design (`COMMIT_COST.md`'s "one-commit lag") `tools/commit_cost/log.py --exclude-current-head` never logs a row for the commit whose hook is currently running; it defers that to the *next* commit's hook. Because the recursion guard stopped one commit early, nothing ever ran a non-excluded pass over the original hand-made commit — it stayed permanently unlogged until `.githooks/pre-commit`'s coverage gate caught it on the *next* real commit attempt, which the session then had to manually resolve.

Net effect: one legitimately-titled manual catch-up commit produced a second, unnecessary auto-commit, and still left a genuine gap that surfaced later as a blocked commit.

## Investigation log

1. Reproduced by reading `.githooks/post-commit` and `.githooks/commit-msg` side by side: `commit-msg`'s `case` pattern is `"Log doc metrics and commit cost for the previous commit"|"Log commit cost for the previous commit"|"Log doc metrics for the previous commit"`; `post-commit`'s `LOG_COMMIT_MSG` variable is a single string equal to only the first of those three.
2. Confirmed the three titles exist because `tools/commit_cost/log.py` and `tools/doc_metrics/log.py` can each independently have nothing new to log — e.g. a `doc_metrics`-only catch-up is a real, valid scenario distinct from the combined case `post-commit` itself always produces.
3. Root cause: the two hooks each hardcode their own copy of "what counts as a catch-up commit title" — `commit-msg` as a 3-way `case`, `post-commit` as a single string — with nothing keeping them in sync. `post-commit` was written assuming it is the *only* thing that ever creates these commits, which stopped being true once a session (reasonably, given `commit-msg` explicitly allows it) hand-commits one of the other two titles.

## Fix

Extracted the three titles into one array (`CATCH_UP_TITLES`) in a new shared file, `.githooks/catch_up_titles.sh`, sourced by both `.githooks/commit-msg` (loops the array instead of a hardcoded `case`) and `.githooks/post-commit` (its recursion guard now checks membership in the array instead of equality against one hardcoded string). A single manual catch-up commit, under any of the three valid titles, no longer triggers a spurious follow-up commit.

## Verified

Reproduced and fixed in an isolated throwaway clone (origin removed, so nothing could push) rather than against the real repo: cloned locally, overlaid the then-uncommitted hook edits, simulated a dropped `commit_costs.jsonl` row, then hand-committed a catch-up titled `Log commit cost for the previous commit` (the previously-broken second title). Result: exactly one commit, went straight to the push step — no spurious follow-up commit, matching the fix's intent. A subsequent trivial real commit then had `pre-commit`'s coverage check pass clean (the catch-up commit's own row was picked up by that next commit's non-excluded `commit_cost/log.py` pass, per the documented one-commit lag) and produced exactly one auto-generated follow-up ledger commit, as designed. `modules/tests` and `contacts/tests` (39 + 19) also still pass against the real repo with the fix applied.

## Security analysis

Change is confined to two local git hooks (`.githooks/commit-msg`, `.githooks/post-commit`) plus a new sourced file (`.githooks/catch_up_titles.sh`) holding a static list of three known commit-title strings — no user input, no network calls, no credentials, no change to what data any hook reads or writes (still only `tools/commit_cost/commit_costs.jsonl` and `tools/doc_metrics/metrics.jsonl`). The only behavior change is *when* the hooks recognize a commit as a catch-up commit; a wider match only ever suppresses an unnecessary auto-commit or lets a legitimately-titled manual commit through the same file-scope check it already enforced. No new attack surface, no residual risk identified.
