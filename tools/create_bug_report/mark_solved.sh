#!/usr/bin/env bash
# Moves a bugs/{repo,claude-bugs}/under_process/*.md file into the matching
# fixed/ folder, marking it resolved. See documentation/bugs/repo/README.md
# and documentation/bugs/claude-bugs/README.md.
#
# Usage:
#   tools/create_bug_report/mark_solved.sh 2026-07-17-thumbnail-oom-under-load.md
#   tools/create_bug_report/mark_solved.sh --claude 2026-07-17-some-lapse.md
set -euo pipefail

CLAUDE_MODE=0
if [ "${1:-}" = "--claude" ]; then
  CLAUDE_MODE=1
  shift
fi

if [ $# -ne 1 ]; then
  echo "Usage: $0 [--claude] <filename.md> (just the filename, not the full path)" >&2
  exit 1
fi

REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

if [ "$CLAUDE_MODE" -eq 1 ]; then
  CATEGORY_DIR="$REPO_ROOT/documentation/bugs/claude-bugs"
else
  CATEGORY_DIR="$REPO_ROOT/documentation/bugs/repo"
fi

SRC="$CATEGORY_DIR/under_process/$1"
FIXED_DIR="$CATEGORY_DIR/fixed"

if [ ! -f "$SRC" ]; then
  echo "Not found: $SRC" >&2
  exit 1
fi

BASENAME="${1%.md}"
if [ "$CLAUDE_MODE" -eq 1 ]; then
  # claude-bugs filenames carry no status suffix - the fixed/ vs
  # under_process/ folder alone conveys resolved status.
  DEST="$FIXED_DIR/${BASENAME}.md"
else
  # repo/ keeps the existing -SOLVED suffix convention so already-solved
  # filenames (and every doc that links to them) don't need renaming too.
  DEST="$FIXED_DIR/${BASENAME}-SOLVED.md"
fi

if [ -e "$DEST" ]; then
  echo "Already exists: $DEST" >&2
  exit 1
fi

mkdir -p "$FIXED_DIR"
git -C "$REPO_ROOT" mv "$SRC" "$DEST"

echo "Moved: $DEST"
