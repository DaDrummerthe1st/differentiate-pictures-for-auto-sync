#!/usr/bin/env bash
# Tests for create_changelog_entry.sh's argument validation, filename
# format, and no-clobber behavior. No framework needed - plain bash
# assertions, run directly:
#   tools/create_changelog_entry/test_create_changelog_entry.sh
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SCRIPT="$SCRIPT_DIR/create_changelog_entry.sh"
REPO_ROOT=$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)
TARGET_DIR="$REPO_ROOT/documentation/changelog"

fail() { echo "FAIL: $1" >&2; exit 1; }

set +e
OUTPUT=$("$SCRIPT" 2>&1)
STATUS=$?
set -e
[ "$STATUS" -ne 0 ] || fail "expected non-zero exit with no title, got 0"
echo "$OUTPUT" | grep -qi "usage" || fail "error message doesn't mention usage, got: $OUTPUT"

BEFORE_COUNT=$(find "$TARGET_DIR" -maxdepth 1 -type f -name '*.md' | wc -l)
CREATED=$("$SCRIPT" "zzz test entry for automated test" | sed -n 's/^Created: //p')
[ -f "$CREATED" ] || fail "expected file to be created at $CREATED"
AFTER_COUNT=$(find "$TARGET_DIR" -maxdepth 1 -type f -name '*.md' | wc -l)
[ "$AFTER_COUNT" -eq "$((BEFORE_COUNT + 1))" ] || fail "expected exactly one new file"

basename "$CREATED" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-zzz-test-entry-for-automated-test\.md$' \
  || fail "unexpected filename format: $(basename "$CREATED")"

rm -f "$CREATED"

echo "All tests passed."
