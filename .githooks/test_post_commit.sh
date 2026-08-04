#!/usr/bin/env bash
# Integration test for .githooks/post-commit, run entirely inside an
# isolated temp repo (a local bare "origin" plus a working clone) so it
# never touches this project's own tools/ or GitHub remote. Stubs stand in
# for tools/doc_metrics/log.py and tools/commit_cost/log.py - the point
# here is the hook's own control flow (recursion guard, push, publishing
# a brand-new branch), not the real logging tools, which already have
# their own test suites.
#
# Run with: .githooks/test_post_commit.sh
set -uo pipefail

fail() { echo "FAIL: $1" >&2; exit 1; }

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
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
# Stub log.py's - just append one line to their own ledger each time
# they're invoked. Whether they're "smart" (dedupe, real parsing) doesn't
# matter for this test; the hook's job is deciding *when* to call them
# and *whether* to auto-commit the result, not what they compute.
cat > tools/doc_metrics/log.py <<'EOF'
open("tools/doc_metrics/metrics.jsonl", "a").write("row\n")
EOF
cat > tools/commit_cost/log.py <<'EOF'
open("tools/commit_cost/commit_costs.jsonl", "a").write("row\n")
EOF
: > tools/doc_metrics/metrics.jsonl
: > tools/commit_cost/commit_costs.jsonl
echo "hello" > content.txt
cp "$POST_COMMIT" .githooks/post-commit
chmod +x .githooks/post-commit

git add -A
git commit -q -m "initial setup" --no-verify
# core.hooksPath set only *after* the setup commit, and upstream
# deliberately left unpublished - the first hook-triggered push below
# must itself establish it (git push -u), matching the real "AI makes a
# brand-new branch's first commit" case Joakim asked about.
git config core.hooksPath .githooks

BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "world" >> content.txt
git add content.txt
git commit -q -m "trigger commit one"

commit_count=$(git log --oneline | wc -l | tr -d ' ')
[ "$commit_count" -eq 3 ] || fail "expected 3 commits after trigger one (setup, trigger, one auto-log), got $commit_count"

last_msg=$(git log -1 --format=%s)
[ "$last_msg" = "Log doc metrics and commit cost for the previous commit" ] \
  || fail "expected HEAD to be the auto-log commit, got: $last_msg"

doc_rows=$(wc -l < tools/doc_metrics/metrics.jsonl | tr -d ' ')
[ "$doc_rows" -eq 1 ] || fail "expected doc_metrics stub invoked exactly once, got $doc_rows row(s) - possible recursion"

remote_head=$(git ls-remote "$BARE" "refs/heads/$BRANCH" | cut -f1)
local_head=$(git rev-parse HEAD)
[ "$remote_head" = "$local_head" ] || fail "expected origin's $BRANCH to match local HEAD after auto-push (first publish), got remote=$remote_head local=$local_head"

# Second cycle - proves the guard resets cleanly and doesn't get stuck
# either always-skipping or always-recursing.
echo "again" >> content.txt
git add content.txt
git commit -q -m "trigger commit two"

commit_count=$(git log --oneline | wc -l | tr -d ' ')
[ "$commit_count" -eq 5 ] || fail "expected 5 commits after trigger two, got $commit_count"

doc_rows=$(wc -l < tools/doc_metrics/metrics.jsonl | tr -d ' ')
[ "$doc_rows" -eq 2 ] || fail "expected doc_metrics stub invoked exactly twice total, got $doc_rows"

remote_head=$(git ls-remote "$BARE" "refs/heads/$BRANCH" | cut -f1)
local_head=$(git rev-parse HEAD)
[ "$remote_head" = "$local_head" ] || fail "expected origin's $BRANCH to match local HEAD after second auto-push, got remote=$remote_head local=$local_head"

echo "All tests passed."
