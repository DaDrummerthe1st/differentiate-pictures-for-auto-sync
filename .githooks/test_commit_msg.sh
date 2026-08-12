#!/usr/bin/env bash
# Integration test for .githooks/commit-msg, run entirely inside an
# isolated temp repo so it never touches this project's own tools/ or
# GitHub remote. Regression test for the lapse documented in
# documentation/bugs/claude-bugs/fixed/2026-08-12-repeated-real-commit-
# bundled-into-mislabeled-commit-cost-catch-up-commit.md (and its
# 2026-08-05 predecessor): a catch-up commit titled as ledger-only must
# actually be ledger-only, mechanically, not by an AI session remembering
# to check.
#
# Run with: .githooks/test_commit_msg.sh
set -uo pipefail

fail() { echo "FAIL: $1" >&2; exit 1; }

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMMIT_MSG_HOOK="$SCRIPT_DIR/commit-msg"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

WORK="$TMP/work"
git init -q "$WORK"
cd "$WORK"
git config user.email "test@example.com"
git config user.name "Test"

mkdir -p tools/doc_metrics tools/commit_cost .githooks
cp "$COMMIT_MSG_HOOK" .githooks/commit-msg
chmod +x .githooks/commit-msg
git config core.hooksPath .githooks

echo "seed" > tools/commit_cost/commit_costs.jsonl
echo "seed" > tools/doc_metrics/metrics.jsonl
git add -A
git commit -q -m "initial setup"

# Case 1: catch-up-titled commit with ONLY the ledger file staged - must
# succeed.
echo "row" >> tools/commit_cost/commit_costs.jsonl
git add tools/commit_cost/commit_costs.jsonl
git commit -q -m "Log doc metrics and commit cost for the previous commit" \
  || fail "ledger-only catch-up commit was blocked but should have succeeded"

# Case 2: catch-up-titled commit with a real file staged alongside the
# ledger file - must be BLOCKED (this is the exact lapse being guarded
# against).
echo "real change" > app_change.txt
echo "row" >> tools/commit_cost/commit_costs.jsonl
git add app_change.txt tools/commit_cost/commit_costs.jsonl
if git commit -q -m "Log commit cost for the previous commit" 2>/tmp/commit_msg_test_stderr; then
  fail "catch-up commit with a non-ledger file staged should have been blocked"
fi
grep -q "BLOCKED" /tmp/commit_msg_test_stderr || fail "expected a BLOCKED message explaining the rejection"
# The bad commit must not have gone through - both files should still be staged.
git diff --cached --name-only | grep -qx "app_change.txt" || fail "app_change.txt should still be staged after the block"

# Clean up the aborted attempt's staged state for the next case.
git reset -q --mixed HEAD

# Case 3: an unrelated commit message must never be checked, regardless
# of what's staged - this hook only ever gates the specific catch-up
# titles, never ordinary commits.
git add app_change.txt tools/commit_cost/commit_costs.jsonl
git commit -q -m "Add a real feature" \
  || fail "an ordinary commit message must never be blocked by this hook"

echo "All tests passed."
