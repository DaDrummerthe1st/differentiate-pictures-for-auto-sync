#!/usr/bin/env bash
# Integration test for .githooks/pre-commit + .githooks/post-commit working
# together, run entirely inside an isolated temp repo (a local bare "origin"
# plus a working clone) so it never touches this project's own tools/ or
# GitHub remote.
#
# Replaces test_post_commit.sh 2026-09-06: doc_metrics/commit_cost logging
# moved from post-commit (a separate auto-generated catch-up commit) into
# pre-commit (folded straight into the commit already being made) - see
# documentation/bugs/repo/fixed/2026-09-06-post-commit-catch-up-commit-skips-logging-the-code-commit-it-exists-to-log-SOLVED.md
# for why the old design had a structural gap. Stubs stand in for
# tools/doc_metrics/log.py and tools/commit_cost/log.py - the point here is
# the hooks' own control flow, not the real logging tools, which already
# have their own test suites. tools/secrets_scan and tools/wrapup_checklist
# are the *real* project code, copied in as-is, since pre-commit's new
# self-healing behavior depends on wrapup_checklist's real coverage logic
# actually seeing the stub-produced rows as valid.
#
# Run with: .githooks/test_commit_hooks.sh
set -uo pipefail

fail() { echo "FAIL: $1" >&2; exit 1; }

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PRE_COMMIT="$SCRIPT_DIR/pre-commit"
POST_COMMIT="$SCRIPT_DIR/post-commit"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

BARE="$TMP/origin.git"
WORK="$TMP/work"

git init -q --bare "$BARE"
git init -q "$WORK"
cd "$WORK"
git remote add origin "$BARE"
git config user.email "test@example.com"
git config user.name "Test"

mkdir -p tools/doc_metrics tools/commit_cost .githooks
cp -r "$REPO_ROOT/tools/secrets_scan" tools/secrets_scan
cp -r "$REPO_ROOT/tools/wrapup_checklist" tools/wrapup_checklist
rm -f tools/secrets_scan/test_scan.py tools/wrapup_checklist/test_checks.py tools/wrapup_checklist/test_run.py
rm -rf tools/secrets_scan/__pycache__ tools/wrapup_checklist/__pycache__

# Stub log.py's - append a real JSON row (with the real current HEAD hash)
# to their own ledger each time they're invoked, deduping by commit_hash
# the same way the real tools do. Whether they compute a *real* char count
# or token cost doesn't matter for this test; the hooks' job is deciding
# *when* to call them and *what to do with the result*, not what they
# compute - that's covered by tools/doc_metrics and tools/commit_cost's own
# test suites.
cat > tools/doc_metrics/log.py <<'PYEOF'
import json, pathlib, subprocess
head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
path = pathlib.Path("tools/doc_metrics/metrics.jsonl")
existing = set()
if path.exists():
    for line in path.read_text().splitlines():
        if line.strip():
            existing.add(json.loads(line)["commit_hash"])
if head not in existing:
    with path.open("a") as f:
        f.write(json.dumps({"commit_hash": head}) + "\n")
PYEOF
cat > tools/commit_cost/log.py <<'PYEOF'
import json, pathlib, subprocess, sys
open("commit_cost_argv.log", "a").write(" ".join(sys.argv[1:]) + "\n")
head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
path = pathlib.Path("tools/commit_cost/commit_costs.jsonl")
existing = set()
if path.exists():
    for line in path.read_text().splitlines():
        if line.strip():
            existing.add(json.loads(line)["commit_hash"])
if head not in existing:
    with path.open("a") as f:
        f.write(json.dumps({"commit_hash": head}) + "\n")
PYEOF
: > tools/doc_metrics/metrics.jsonl
: > tools/commit_cost/commit_costs.jsonl
echo "hello" > content.txt
cp "$PRE_COMMIT" .githooks/pre-commit
cp "$POST_COMMIT" .githooks/post-commit
chmod +x .githooks/pre-commit .githooks/post-commit

git add -A
git commit -q -m "initial setup" --no-verify
# core.hooksPath set only *after* the setup commit, and upstream
# deliberately left unpublished - the first hook-triggered push below must
# itself establish it (git push -u), matching the real "AI makes a
# brand-new branch's first commit" case Joakim asked about. This also means
# "initial setup" itself never gets a ledger row (pre-commit never ran for
# it) - deliberately mirrors this real repo's own history, whose earliest
# commits predate the ledgers entirely.
git config core.hooksPath .githooks

BRANCH=$(git rev-parse --abbrev-ref HEAD)
initial_setup_hash=$(git rev-parse HEAD)

echo "world" >> content.txt
git add content.txt
git commit -q -m "trigger commit one"

commit_count=$(git log --oneline | wc -l | tr -d ' ')
[ "$commit_count" -eq 2 ] || fail "expected exactly 2 commits after trigger one (setup, trigger - no separate catch-up commit), got $commit_count"

last_msg=$(git log -1 --format=%s)
[ "$last_msg" = "trigger commit one" ] || fail "expected HEAD to still be the real commit, not an auto-generated one, got: $last_msg"

doc_rows=$(git show HEAD:tools/doc_metrics/metrics.jsonl | grep -c "$initial_setup_hash")
[ "$doc_rows" -eq 1 ] || fail "expected trigger-commit-one's own tree to already contain a logged row for its parent (initial setup), got $doc_rows"

remote_head=$(git ls-remote "$BARE" "refs/heads/$BRANCH" | cut -f1)
local_head=$(git rev-parse HEAD)
[ "$remote_head" = "$local_head" ] || fail "expected origin's $BRANCH to match local HEAD after auto-push (first publish), got remote=$remote_head local=$local_head"

trigger_one_hash="$local_head"

# Second cycle - proves this isn't a one-shot: the *next* commit correctly
# catches up trigger-commit-one's own row (deferred by exactly one commit,
# same as before), still with no separate commit ever created.
echo "again" >> content.txt
git add content.txt
git commit -q -m "trigger commit two"

commit_count=$(git log --oneline | wc -l | tr -d ' ')
[ "$commit_count" -eq 3 ] || fail "expected exactly 3 commits after trigger two, got $commit_count"

doc_rows_total=$(git show HEAD:tools/doc_metrics/metrics.jsonl | wc -l | tr -d ' ')
[ "$doc_rows_total" -eq 2 ] || fail "expected 2 total logged rows (initial setup + trigger one) after trigger two, got $doc_rows_total"
git show HEAD:tools/doc_metrics/metrics.jsonl | grep -q "$trigger_one_hash" \
  || fail "expected trigger-commit-one's own row to be caught up by trigger-commit-two's pre-commit run"

remote_head=$(git ls-remote "$BARE" "refs/heads/$BRANCH" | cut -f1)
local_head=$(git rev-parse HEAD)
[ "$remote_head" = "$local_head" ] || fail "expected origin's $BRANCH to match local HEAD after second auto-push, got remote=$remote_head local=$local_head"

# Regression guard for the 2026-09-06 bug: commit_cost/log.py must be
# invoked plain, never with --exclude-current-head, now that the call
# happens one step earlier (pre-commit, against the already-completed
# parent commit) instead of against the commit whose own transcript is
# still in flight.
grep -q -- '--exclude-current-head' commit_cost_argv.log \
  && fail "commit_cost/log.py should no longer be invoked with --exclude-current-head"

# Extended regression guard: repeat for several more commits in a row with
# no manual intervention - the original bug only ever surfaced on the
# commit *after* a catch-up commit existed, so a single before/after pair
# isn't enough to trust this is fixed for good.
for i in 3 4 5 6; do
  echo "round $i" >> content.txt
  git add content.txt
  git commit -q -m "trigger commit $i"
done

commit_count=$(git log --oneline | wc -l | tr -d ' ')
[ "$commit_count" -eq 7 ] || fail "expected exactly 7 commits after 4 more rounds (1 initial + 6 triggers, still no catch-up commits), got $commit_count"

remote_head=$(git ls-remote "$BARE" "refs/heads/$BRANCH" | cut -f1)
local_head=$(git rev-parse HEAD)
[ "$remote_head" = "$local_head" ] || fail "expected origin's $BRANCH to match local HEAD after the extended round, got remote=$remote_head local=$local_head"

echo "All tests passed."
