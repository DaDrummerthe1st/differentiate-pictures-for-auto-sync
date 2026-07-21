#!/usr/bin/env bash
# Tests for create_bug_report.sh's argument validation. No framework needed -
# plain bash assertions, run directly: tools/create_bug_report/test_create_bug_report.sh
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SCRIPT="$SCRIPT_DIR/create_bug_report.sh"
REPO_ROOT=$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)

fail() { echo "FAIL: $1" >&2; exit 1; }

# --claude in the wrong position (after the title) must error clearly,
# not silently get absorbed into the title text - fixed 2026-07-18 after
# it wasted time creating a wrongly-named file, see CHANGELOG.
BEFORE_COUNT=$(find "$REPO_ROOT/documentation/bugs/claude-bugs/under_process" "$REPO_ROOT/documentation/bugs/repo/under_process" -type f | wc -l)
set +e
OUTPUT=$("$SCRIPT" "test misplaced flag title zzz" --claude 2>&1)
STATUS=$?
set -e
AFTER_COUNT=$(find "$REPO_ROOT/documentation/bugs/claude-bugs/under_process" "$REPO_ROOT/documentation/bugs/repo/under_process" -type f | wc -l)

[ "$STATUS" -ne 0 ] || fail "expected non-zero exit when --claude is misplaced, got 0"
[ "$AFTER_COUNT" -eq "$BEFORE_COUNT" ] || fail "a file was created despite the misplaced --claude flag"
echo "$OUTPUT" | grep -qi -- "--claude" || fail "error message doesn't mention --claude, got: $OUTPUT"

echo "All tests passed."
