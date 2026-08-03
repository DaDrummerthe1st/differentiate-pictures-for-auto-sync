# Missed doc_metrics/commit_cost logging for 3 commits

## What happened

After the session's earlier wrap-up round, three more commits went out (`cca8a47`, `6b3315d`, `41a2073`) without the `tools/doc_metrics`/ `tools/commit_cost` logging step that CLAUDE.md requires after every commit. Joakim caught the gap by asking directly, not something I noticed myself.

## Why it happened

Mid-session momentum — several fast-moving fixes in a row (a bug report correction, then a policy add-then-revert cycle) and the logging step quietly stopped being part of the loop, with no explicit checkpoint forcing it back in.

## What changed

`tools/commit_cost/check_coverage.sh` added (2026-07-17) — a script that compares every commit hash in `git log` against `commit_costs.jsonl` and reports any missing, so this class of gap is now a one-command check rather than something that has to be noticed by inspection. Wired into the session wrap-up routine (CLAUDE.md).

## Recurrence #1 (2026-08-03) — the fix only covered half the original bug

While logging doc_metrics/commit_cost for this session's own commits, running `tools/doc_metrics/log.py --backfill` (safe to rerun, dedupes by commit hash) surfaced **220 previously-unlogged commits** in `tools/doc_metrics/metrics.jsonl` (251 of 474 commits had a row; 471 after backfill, the remaining 3 being commits before any `.md` file existed in the repo). `commit_cost/check_coverage.sh` reported clean the whole time — because it only ever checked `commit_costs.jsonl`, not `metrics.jsonl`. The 2026-07-17 fix built a coverage check for one of the two logging tools this bug's own title names and silently left the other with no equivalent, so the same underlying lapse (a post-commit logging step quietly falling out of the loop, with nothing to catch it) kept recurring for `doc_metrics` specifically across roughly three weeks of commits, undetected.

**What changed this time**: `tools/doc_metrics/check_coverage.sh` added — same design as `commit_cost`'s (compares every commit in `git log` against the jsonl, reports any missing), with one adjustment: a commit with zero tracked `*.md` files at that point in history is a real, expected absence (this repo's earliest commits, before any documentation existed), not a gap, so those are excluded from the count rather than flagged. Wired into `documentation/tooling/README.md`'s session wrap-up checklist as its own row, distinct from the `commit_cost` one — the lesson from this recurrence is that "we already have a coverage check" isn't a safe inference from one tool to a similarly-named sibling tool; each logging mechanism needs its own explicit coverage check, named as such.
