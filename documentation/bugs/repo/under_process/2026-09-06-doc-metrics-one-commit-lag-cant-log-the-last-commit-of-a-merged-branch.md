# doc_metrics' one-commit-lag design can't log the last commit of a branch that gets merged

Status: **investigating, backfilled but not structurally fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Merging `android-app-test1` into `master` (`git merge --no-ff`, 13 commits, clean/no conflicts),
then trying to commit the follow-up archival change (`git mv android/ previous-work/kotlin/` +
doc updates) got permanently blocked by `.githooks/pre-commit`'s coverage gate:

```
[MISSING] doc_metrics: 1 *.md-touching commit(s) with no logged row (run tools/doc_metrics/log.py):
  55ecd55aabb9e8b13a44b032cc160b6d160f537b
[pre-commit] coverage gap remains even after self-healing - this shouldn't happen; investigate
tools/doc_metrics/log.py or tools/commit_cost/log.py directly.
```

`55ecd55` was the last commit made on `android-app-test1` before merging it - a real, already
hook-verified commit (its own pre-commit run had passed cleanly). Running plain
`python3 tools/doc_metrics/log.py` (what the pre-commit hook itself calls) every time still left
this one row missing, no matter how many times the "self-healing" step ran.

## Investigation log

1. Confirmed via `git log --oneline -5` that `HEAD` was the merge commit itself (bringing 13
   commits in as its second-parent history), and via `grep -c 55ecd55 tools/doc_metrics/metrics.jsonl`
   that the row was genuinely, persistently absent (not a transient race).
2. Read `tools/doc_metrics/log.py`: its default invocation (`log_current_commit()`, no flags -
   exactly what `.githooks/pre-commit` calls) logs **only the single current `HEAD` commit** as a
   whole-tree snapshot. There is no gap-scan across multiple missing commits in that path - only
   `--backfill` does that, and nothing calls `--backfill` automatically.
3. Read `tools/commit_cost/log.py` for comparison: its `log_new_commits()` walks `git log --pretty=%H`
   (every commit reachable from `HEAD`) and computes `candidates_for_logging()` against what's
   already in the ledger - a full gap-scan, every single invocation. This is why `commit_cost`
   *did* correctly backfill `55ecd55` (confirmed a real row for it, with actual transcript-matched
   token cost, appeared in `commit_costs.jsonl` right after the failed commit attempt) while
   `doc_metrics` did not: the two self-healing scripts don't actually use the same strategy,
   despite `.githooks/pre-commit`'s comment implying they're symmetric ("log.py in both tools/ is
   idempotent... running it on every commit is safe").
4. Root cause has two parts that compound:
   - **`git merge` doesn't invoke `pre-commit` at all** for a clean, non-conflicting merge (a
     documented git behavior, not a bug in this repo) - so the merge commit itself never got a
     chance to trigger the self-healing step at the moment it was created.
   - **`doc_metrics/log.py`'s one-commit-lag design** (see `documentation/tooling/DOC_METRICS.md`)
     relies on every commit eventually becoming "the previous commit" at some *later* commit's
     pre-commit run. `55ecd55` was the last commit made on `android-app-test1` - no further commit
     was ever made on that branch, so its one-commit-lag "turn" never came. Once the branch was
     merged, `master`'s own commit chain jumps straight from the merge commit onward; `55ecd55`
     is reachable in `git log` (so `commit_cost`'s full-scan design finds it) but is never itself
     `HEAD` at any subsequent linear commit on `master` (so `doc_metrics`'s HEAD-only design never
     finds it).
   - Together: **the terminal commit of any branch merged via a real merge commit is structurally
     unloggable by `doc_metrics/log.py`'s current design**, not a one-off glitch. This is the first
     time this repo did a real feature-branch merge since the self-healing redesign in
     [2026-09-06-post-commit-catch-up-commit-skips-logging-the-code-commit-it-exists-to-log-SOLVED.md](../fixed/2026-09-06-post-commit-catch-up-commit-skips-logging-the-code-commit-it-exists-to-log-SOLVED.md)
     (that fix's own test suite, `.githooks/test_commit_hooks.sh`, only exercises linear
     commit-after-commit sequences, never a merge) - so this gap existed unnoticed since that fix.

## Workaround applied

Ran `python3 tools/doc_metrics/log.py --backfill` by hand (safe/idempotent - `persist_snapshot`
skips any `commit_hash` already present via `_jsonl_has_commit`) to catch up `55ecd55` and confirm
no other historical gaps exist, then re-ran `tools/wrapup_checklist/run.py --coverage-only` to
confirm the gate passes before retrying the blocked commit.

## Next session should start with

- Decide the actual fix: either make `doc_metrics/log.py`'s default (non-`--backfill`) mode do the
  same kind of full gap-scan `commit_cost/log.py` already does (probably the right call - they're
  meant to be symmetric per `.githooks/pre-commit`'s own comment), or have `.githooks/pre-commit`
  call `--backfill` instead of the bare no-arg form. A full-history `--backfill` re-reads every
  `.md` file at every past commit via `git show` and is noticeably slow (multiple minutes over
  ~320 commits) - worth checking whether it can be scoped to "commits since the last logged one"
  rather than the entire history, to stay cheap enough to run on every commit.
- Add a merge scenario to `.githooks/test_commit_hooks.sh` (currently only linear commits) so this
  class of gap gets caught by the test suite instead of live, mid-session.
- Confirm whether any other historical merge (this repo has several, per `git log --oneline
  --merges`) left a similar orphaned commit in `doc_metrics` - the backfill run above should have
  caught any that exist, but wasn't specifically audited row-by-row for that.
