# tools/commit_cost stops finding commit boundaries partway through a long session

Status: **investigating, not fixed**.

## Symptom

Found 2026-07-17, live: after this session's commits stopped showing
real token/cost data and started logging as "human-only, 0 tokens"
(despite every commit being AI-made), direct testing of
`tools/commit_cost/metrics.py`'s `group_events_by_commit` against this
session's own transcript file (`~/.claude/projects/.../d7c0f69a-*.jsonl`)
showed it only found boundaries for the *first 5* commits of a much
longer session (roughly the first 40% by commit count) — nothing after
that, even though the transcript keeps growing and more `git commit`
tool calls clearly happened.

## Investigation log

1. Noticed `commit_costs.jsonl` logging "0 LLM-assisted, N human-only"
   repeatedly despite every commit being AI-authored this session.
2. Directly invoked `find_commit_boundaries`/`group_events_by_commit`
   against the live transcript file matching this session's ID.
3. Confirmed: only 5 of many commit boundaries found, all from early in
   the session (`9c090b0` through `df22cbc`).
4. Reproduced again later in the same session on two more commits —
   confirmed not a one-off fluke.

## Leading theory (unconfirmed)

`find_commit_boundaries` scans for a `git commit` tool_use followed by
its tool_result containing a short hash; something about that matching
breaks down partway through this one session. `metrics.py` already has
a comment noting `"<synthetic>"` rows appear "after compaction" — a
very long single session hitting context compaction partway through is
the leading theory for what changes structurally at that point, not
confirmed.

## Practical impact

`commit_costs.jsonl` likely undercounts real spend for any long-running
single session, silently (it logs a confident "0 tokens, human-only"
rather than failing loudly).

## Next session should start with

Diff the transcript's row structure before vs. after the point
boundary-detection stops working, not more guessing.

## Related: this bug is itself a signal for when to wrap up

Noted by Joakim 2026-07-18: since this bug's root cause is tied to
session length (a "very long single session hitting context compaction"
is the leading unconfirmed theory above), **this bug starting to
manifest is itself a practical signal that a session has run long
enough to consider wrapping up** - not just a symptom to work around.
If `commit_costs.jsonl` starts showing "0 tokens, human-only" for
commits that are obviously AI-authored, that's as much a "this session
is getting long" alarm as it is a tooling bug to fix later.
