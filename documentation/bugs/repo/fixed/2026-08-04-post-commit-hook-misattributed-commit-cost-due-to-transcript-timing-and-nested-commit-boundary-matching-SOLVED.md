# Post-commit hook misattributed commit_cost due to transcript timing and nested-commit boundary matching

Status: **fixed 2026-08-04**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Right after building `.githooks/post-commit` (auto-logs `doc_metrics`/`commit_cost`
after every commit, then pushes), the commit that introduced the hook itself
(`18f8b647e6df776f3e4df79157e23316a6852c5d`, "Auto-log ledgers and push after every
commit via post-commit hook") got logged in `commit_costs.jsonl` as
`llm_session_found: false, cost_usd: 0.0` — a real, LLM-authored commit recorded as
genuinely human-only.

## Investigation log

1. `commit_cost/log.py` resolves a commit's cost by finding, in the live session
   transcript, the `tool_result` paired with the `Bash` `git commit` `tool_use` -
   see `find_commit_boundaries` (`metrics.py:109-135`).
2. The post-commit hook runs `tools/commit_cost/log.py` from *inside* the same
   Bash tool call that just created the triggering commit. The harness only
   appends that Bash call's `tool_result` row to the transcript file after the
   *entire* call (hook included) finishes - so at hook-execution time, the
   transcript literally doesn't contain this commit's boundary text yet.
   `collect_commit_costs` finds nothing, and the commit falls into the
   "no session touched this" branch, which is correct for a genuinely human
   commit but wrong here - the data just isn't written yet.
3. Confirmed by manually re-checking minutes later, once the enclosing Bash tool
   call had long since completed: `collect_commit_costs(...).get('18f8b64')`
   still returned `None`, even though `grep` found the boundary text
   `[master 18f8b64] ...` in the transcript file on disk.
4. Root-caused the *second* issue this revealed: the post-commit hook itself runs
   a *nested* `git commit` (auto-logging the previous commit) from inside the
   outer commit's own Bash call. Git only prints the *outer*, directly-invoked
   commit's own `[branch hash]` confirmation line after all of its hooks
   (including that nested commit's full lifecycle) finish - so the nested
   commit's line always appears *earlier* in the combined `tool_result` text,
   the outer/real one always *last*. `_COMMIT_HASH_RE.search(text)` (first
   match) was grabbing the nested, auto-generated commit's hash instead of the
   real outer one. Verified directly against the real transcript: the tool_result
   for the Bash call that created `18f8b64` contained, in order, `[master
   31122a9] Log doc metrics and commit cost for the previous commit` (the nested
   auto-log commit) *then* `[master 18f8b64] Auto-log ledgers and push after
   every commit via post-commit hook` (the real, outer commit) - `.search()`
   picked `31122a9`, found no matching `tool_use` for that hash at all (it isn't
   a real Claude `tool_use`, just shell output), so nothing was attributed to it
   either, and the real commit's usage was never resolved.

## Leading theory (confirmed)

Two independent, compounding causes: (1) `commit_cost/log.py` invoked *from
inside* a still-running `git commit`'s hook can never resolve that commit's own
boundary, because the transcript row for it doesn't exist yet at that point. (2)
`find_commit_boundaries` took the *first* regex match in a `tool_result`, which
is wrong whenever that Bash call's `git commit` itself triggers a *nested*
`git commit` (via `.githooks/post-commit`) - the nested commit's confirmation
line is always printed first, the outer/real one always last.

## What changed

- `tools/commit_cost/metrics.py::candidates_for_logging()` (new, tested in
  `test_metrics.py`) lets a caller exclude the single newest commit hash from a
  logging run. `.githooks/post-commit` now calls
  `python3 tools/commit_cost/log.py --exclude-current-head`, deferring the
  triggering commit's own row to the *next* commit's hook run, by which point
  the transcript boundary exists.
- `find_commit_boundaries` now takes the *last* regex match in a `tool_result`,
  not the first (`metrics.py`, `_COMMIT_HASH_RE.finditer` instead of `.search`) -
  tested in `test_metrics.py::test_a_hook_triggered_nested_commit_does_not_shadow_the_outer_one`.
  This generalizes correctly to arbitrarily nested hook-triggered commits, since
  git always prints the directly-invoked commit's own confirmation line last,
  after all of its own hooks (including any nested commits) finish.
- **Data correction**: `commit_costs.jsonl`'s existing wrong row for `18f8b64`
  was replaced in place with the real, now-resolvable data (`claude-sonnet-5`,
  14,727,716 total billed tokens, $12.0069 — real numbers, not estimated) rather
  than left as a documented-but-wrong artifact. Reasoning for correcting rather
  than leaving it (unlike `DOC_METRICS.md`'s own precedent of leaving old,
  widely-relied-upon historical pollution as-is): this was a single row,
  mechanically and demonstrably wrong (not a debatable methodology difference),
  discovered and corrected within the same session that created it, before
  anything downstream had relied on the number - and `commit_costs.jsonl`'s
  entire declared purpose is the *honest* real cost, which a known-false `$0`
  actively contradicts. The nested auto-log commit `31122a9` then got its own,
  correctly-`$0`/`llm_session_found: false` row via a normal `log.py` run - this
  one actually is honest: an auto-generated commit with no `tool_use` of its own
  genuinely costs nothing additional, since its cost is already fully counted
  inside the outer commit's segment.

## Security analysis

Pure data-processing/git-tooling change - no user input, network access, or
credentials involved; `commit_costs.jsonl` already only ever stores commit
hashes, numeric token/cost fields, model names, and session UUIDs (see
`COMMIT_COST.md`'s "Privacy" section), unaffected by this fix. The one-time
manual correction of `18f8b64`'s row was a direct, reviewed in-place edit to a
git-tracked file, not a scripted/automatic rewrite - no risk of silently
altering other rows. No other attack surface touched.
