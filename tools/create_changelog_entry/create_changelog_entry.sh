#!/usr/bin/env bash
# Creates a new, consistently-named changelog entry file with a starter
# template - one file per entry, always, never appended to a shared
# growing file. See documentation/changelog/README.md.
#
# Usage:
#   tools/create_changelog_entry/create_changelog_entry.sh "Short entry title"
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 \"Short entry title\"" >&2
  exit 1
fi

TITLE="$*"
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//')
TIMESTAMP=$(date -u +%Y-%m-%dT%H-%M-%SZ)
REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

TARGET_DIR="$REPO_ROOT/documentation/changelog"
FILE="$TARGET_DIR/$TIMESTAMP-$SLUG.md"

if [ -e "$FILE" ]; then
  echo "Already exists: $FILE" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

cat > "$FILE" <<EOF
# $TITLE

What + why, one or two lines.

- **Doc size**: ...
EOF

echo "Created: $FILE"
