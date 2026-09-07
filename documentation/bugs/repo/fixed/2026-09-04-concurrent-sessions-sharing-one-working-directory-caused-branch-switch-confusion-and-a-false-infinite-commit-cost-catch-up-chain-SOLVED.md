# Concurrent sessions sharing one working directory caused branch-switch confusion and a false infinite commit_cost catch-up chain

Status: **fixed**.

## Symptom

While renaming `modules/quality.py`'s functions (this session, on `master`), the pre-commit `commit_cost` coverage check blocked the real commit and kept demanding another `tools/commit_cost/log.py --exclude-current-head` + "Log commit cost for the previous commit" catch-up round after every catch-up round — 5+ rounds deep, each one a real commit (some logged with non-zero session cost, e.g. $3.52 and $0.26), with no sign of terminating. Looked like the ledger-chaining design (`candidates_for_logging`'s `exclude_head` in `tools/commit_cost/metrics.py`) has no fixed point once commits are made back-to-back within one session.

Mid-chase, `git branch --show-current` turned out to be `test_production1`, not `master` — this session never ran `git checkout`. `git log --oneline --graph` showed a `Merge master into test_production1` commit (`ad2829d`) appears mid-chain, made by another Claude Code session the user confirmed was running concurrently in the same repo checkout (no git worktree isolation between sessions). That other session's own commits/checkouts on the shared working directory interleaved with this session's `git commit` calls, which is what made the chain look unbounded — it wasn't one session's hook looping forever, it was two sessions' commits racing on the same ledger file and branch pointer.

## Investigation log

1. Confirmed the rename commit itself (`ebdffa2`) landed fine and is an ancestor of both `origin/master` and `origin/test_production1` — no work was lost, both branches ended up in sync with their remotes (`git rev-list --left-right --count test_production1...origin/test_production1` → `0 0`; local `master` == `origin/master` tip `e110c35`).
2. Did not dig further into *why* the shared checkout's branch changed under this session — the user confirmed a second session was active and has since told it to wrap up. Root cause (exact mechanism by which the other session's branch switch became visible mid-command to this session) not isolated.
3. Did not determine whether `tools/commit_cost`'s post-commit hook chain (each commit spawning a "Log doc metrics and commit cost for the previous commit" follow-up commit) is *itself* safe under two concurrent `git commit` processes in the same `.git` directory, or whether that's a second, independent source of races (lock contention, interleaved reads of `commit_costs.jsonl` producing duplicate/skipped rows). Worth checking `tools/commit_cost/commit_costs.jsonl` and `tools/doc_metrics/metrics.jsonl` for duplicate or out-of-order `commit_hash` rows from this session's timeframe (~2026-09-04T16:40Z-16:50Z).

## Leading theory (unconfirmed)

This repo has no isolation between concurrent Claude Code sessions working in the same directory — no `git worktree`, no per-session branch/clone convention. Two sessions running `git commit`/`git checkout`/`git push` against the same working tree and `.git` will see each other's branch switches and commits interleaved, which is confusing at best (this incident) and could plausibly corrupt the commit_cost/doc_metrics ledger at worst (unverified — see investigation item 3).

## Next session should start with

- Check `tools/commit_cost/commit_costs.jsonl` and `tools/doc_metrics/metrics.jsonl` for any duplicate/malformed rows around the 2026-09-04T16:40-16:50Z window (both `master` and `test_production1` share this history now via the merge).
- Decide whether concurrent sessions need an explicit convention (e.g. one session per git worktree, or "ask before running git commands if another session may be active") and, if so, add it to CLAUDE.md/WORKFLOW.md - that would be the fix that lets this move to `fixed/`.
- Confirm with Joakim whether the other session's `test_production1` branch and its `archive/` untracked directory (seen sitting in the shared working tree after this incident) are intentional in-progress work, not something to clean up unprompted.

## What changed

Added an explicit convention to `WORKFLOW.md`'s "Other standing rules" (2026-09-07): check `git branch --show-current` and use `ListAgents`/`SendMessage` to check for an active peer session before concluding unexpected git/hook state is a tooling bug, escalate genuinely conflicting strategic direction to Joakim via `AskUserQuestion`, and prefer a dedicated worktree/branch for genuinely separate subsystem work. This recurred once more on 2026-09-06/07 (a Kotlin-vs-React conflicting-instructions incident, not just git-state confusion) before the rule was written down — the pattern (check for peers, don't assume) held up and was folded into the same rule rather than filed separately. The `commit_costs.jsonl`/`metrics.jsonl` duplicate-row check and the `test_production1`/`archive/` cleanup question from "Next session should start with" were not separately investigated — no further symptoms of either were observed in the sessions since, treated as non-blocking for closing this out.

## Security analysis

The fix is a process rule (check for peers before assuming a tooling bug), not a code/config change — no attack surface or data handling is affected. Residual risk: the fix is judgment-dependent (an AI session choosing to run `ListAgents` and read git state before theorizing), not mechanically enforced — a future session could still skip it under time pressure, same class of risk [[user_wants_honest_capability_limits]] already names for judgment-based fixes generally. No git/commit-ledger corruption from concurrent writes was ever confirmed (investigation item 3 was never completed) — if `commit_costs.jsonl`/`metrics.jsonl` integrity under concurrent writes becomes a real concern later, that's a distinct, still-open question, not resolved by this fix.
