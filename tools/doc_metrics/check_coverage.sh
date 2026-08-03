#!/usr/bin/env bash
# Verifies every commit in git log has a corresponding entry in metrics.jsonl -
# catches the doc_metrics half of the gap found 2026-07-17 (commit_cost got its
# own check_coverage.sh that day; doc_metrics never did, and silently
# accumulated a 220-commit gap discovered 2026-08-03). Run this as part of
# session wrap-up, not just "ran log.py, assumed it caught everything."
#
# A commit with zero *.md files in its tree at that point (this repo's
# earliest commits, before any documentation existed) never gets a jsonl row
# at all - that's a real, expected absence, not a gap, so it's excluded from
# the count rather than reported as missing.
set -euo pipefail

REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$REPO_ROOT"

JSONL="tools/doc_metrics/metrics.jsonl"

if [ ! -f "$JSONL" ]; then
  echo "MISSING: $JSONL does not exist" >&2
  exit 1
fi

missing=0
while read -r hash; do
  md_count=$(git ls-tree -r --name-only "$hash" | grep -c '\.md$' || true)
  if [ "$md_count" -eq 0 ]; then
    continue
  fi
  if ! grep -q "\"commit_hash\": \"$hash\"" "$JSONL"; then
    echo "MISSING from metrics.jsonl: $hash ($(git log -1 --format=%s "$hash"))"
    missing=$((missing + 1))
  fi
done < <(git log --pretty=%H)

if [ "$missing" -eq 0 ]; then
  echo "OK: every commit with tracked *.md files has a metrics.jsonl entry."
else
  echo
  echo "$missing commit(s) missing - run tools/doc_metrics/log.py --backfill to catch up."
  exit 1
fi
