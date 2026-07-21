# Missed doc_metrics/commit_cost logging for 3 commits

## What happened

After the session's earlier wrap-up round, three more commits went out (`cca8a47`, `6b3315d`, `41a2073`) without the `tools/doc_metrics`/ `tools/commit_cost` logging step that CLAUDE.md requires after every commit. Joakim caught the gap by asking directly, not something I noticed myself.

## Why it happened

Mid-session momentum — several fast-moving fixes in a row (a bug report correction, then a policy add-then-revert cycle) and the logging step quietly stopped being part of the loop, with no explicit checkpoint forcing it back in.

## What changed

`tools/commit_cost/check_coverage.sh` added (2026-07-17) — a script that compares every commit hash in `git log` against `commit_costs.jsonl` and reports any missing, so this class of gap is now a one-command check rather than something that has to be noticed by inspection. Wired into the session wrap-up routine (CLAUDE.md).
