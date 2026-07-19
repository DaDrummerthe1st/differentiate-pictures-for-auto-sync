#!/usr/bin/env bash
# Moves a documentation/bugs/reports/*.md file to documentation/bugs/solved/,
# renaming it to mark it solved. See documentation/bugs/solved/README.md.
#
# Usage:
#   tools/create_bug_report/mark_solved.sh 2026-07-17-thumbnail-oom-under-load.md
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <report-filename.md> (just the filename, not the full path)" >&2
  exit 1
fi

REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
SRC="$REPO_ROOT/documentation/bugs/reports/$1"
SOLVED_DIR="$REPO_ROOT/documentation/bugs/solved"

if [ ! -f "$SRC" ]; then
  echo "Not found: $SRC" >&2
  exit 1
fi

BASENAME="${1%.md}"
DEST="$SOLVED_DIR/${BASENAME}-SOLVED.md"

if [ -e "$DEST" ]; then
  echo "Already exists: $DEST" >&2
  exit 1
fi

mkdir -p "$SOLVED_DIR"
git -C "$REPO_ROOT" mv "$SRC" "$DEST"

echo "Moved: $DEST"
