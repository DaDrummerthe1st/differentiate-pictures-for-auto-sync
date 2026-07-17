#!/usr/bin/env bash
# Creates a new dated, consistently-named bug file with a starter
# template - one file per bug, always, never a bullet added to a shared
# list. See documentation/bugs/README.md and documentation/bugs/claude/README.md.
#
# Usage:
#   tools/new_bug_report/new_bug_report.sh "Thumbnail OOM under load"
#   tools/new_bug_report/new_bug_report.sh --claude "Missed commit_cost logging"
set -euo pipefail

CLAUDE_MODE=0
if [ "${1:-}" = "--claude" ]; then
  CLAUDE_MODE=1
  shift
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 [--claude] \"Short bug title\"" >&2
  exit 1
fi

TITLE="$*"
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')
DATE=$(date +%Y-%m-%d)
REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

if [ "$CLAUDE_MODE" -eq 1 ]; then
  TARGET_DIR="$REPO_ROOT/documentation/bugs/claude"
else
  TARGET_DIR="$REPO_ROOT/documentation/bugs/reports"
fi
FILE="$TARGET_DIR/$DATE-$SLUG.md"

if [ -e "$FILE" ]; then
  echo "Already exists: $FILE" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

if [ "$CLAUDE_MODE" -eq 1 ]; then
  cat > "$FILE" <<EOF
# $TITLE

A routine that should have run per an existing rule, and didn't - or a
claim made without properly checking it first. See
[README.md](README.md) for what belongs here.

## What happened

...

## Why it happened

...

## What changed

(a CLAUDE.md rule tightened, a routine made more explicit, a check
added - every entry here should end with something that actually
changed, not just a description of the lapse)
EOF
  echo "Created: $FILE"
  echo "Add a one-line pointer to it from documentation/bugs/claude/README.md's index."
else
  cat > "$FILE" <<EOF
# $TITLE

Status: **investigating, not fixed**. See [../TODO.md](../TODO.md) for
the index of all open bugs - keep this file as the full chronological
trail, don't overwrite conclusions as more is learned.

## Symptom

(what's actually observed - be concrete, include exact error text/status
codes where possible)

## Investigation log

1. ...

## Leading theory (unconfirmed)

...

## Next session should start with

...
EOF
  echo "Created: $FILE"
  echo "Add a one-line pointer to it from documentation/bugs/TODO.md's index."
fi
