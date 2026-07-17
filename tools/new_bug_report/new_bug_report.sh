#!/usr/bin/env bash
# Creates a new documentation/bugs/reports/<date>-<slug>.md file with a
# consistent name and starter template. See documentation/bugs/README.md.
#
# Usage:
#   tools/new_bug_report/new_bug_report.sh "Thumbnail OOM under load"
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 \"Short bug title\"" >&2
  exit 1
fi

TITLE="$*"
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')
DATE=$(date +%Y-%m-%d)
REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
REPORTS_DIR="$REPO_ROOT/documentation/bugs/reports"
FILE="$REPORTS_DIR/$DATE-$SLUG.md"

if [ -e "$FILE" ]; then
  echo "Already exists: $FILE" >&2
  exit 1
fi

mkdir -p "$REPORTS_DIR"
cat > "$FILE" <<EOF
# $TITLE

Status: **investigating, not fixed**. Short version belongs in
[../TODO.md](../TODO.md); this file is the full chronological trail —
update it as more is learned, don't just overwrite conclusions.

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
echo "Add a one-line pointer to it from documentation/bugs/TODO.md."
