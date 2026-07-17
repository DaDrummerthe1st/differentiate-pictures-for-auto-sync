#!/usr/bin/env bash
# Verifies every commit in git log has a corresponding entry in
# commit_costs.jsonl - catches the exact gap found 2026-07-17 (3 commits
# never logged, silently, for a stretch of a session). Run this as part
# of session wrap-up, not just "ran log.py, assumed it caught everything."
set -euo pipefail

REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$REPO_ROOT"

JSONL="tools/commit_cost/commit_costs.jsonl"

if [ ! -f "$JSONL" ]; then
  echo "MISSING: $JSONL does not exist" >&2
  exit 1
fi

missing=0
while read -r hash; do
  if ! grep -q "\"commit_hash\": \"$hash\"" "$JSONL"; then
    echo "MISSING from commit_costs.jsonl: $hash ($(git log -1 --format=%s "$hash"))"
    missing=$((missing + 1))
  fi
done < <(git log --pretty=%H)

if [ "$missing" -eq 0 ]; then
  echo "OK: every commit has a commit_costs.jsonl entry."
else
  echo
  echo "$missing commit(s) missing - run tools/commit_cost/log.py to catch up."
  exit 1
fi
