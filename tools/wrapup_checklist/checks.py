"""Pure logic for the mechanical subset of the session wrap-up checklist
(documentation/tooling/README.md's table) - raised in
documentation/tooling/TODO.md 2026-07-19: the checklist relied on a session
reading and remembering it correctly every time, the same failure mode the
now-retired tools/commit_cost/check_coverage.sh and
tools/doc_metrics/check_coverage.sh shell scripts were built to close for
their own numbers (see COMMIT_COST.md / DOC_METRICS.md). This module is now
the single implementation both ledgers' coverage checks share. See
../../documentation/tooling/WRAPUP_CHECKLIST.md for which rows this
actually covers - several of the table's checks are genuine judgment calls
that no script can make, and are surfaced as reminders, not pass/fail.
"""
from __future__ import annotations

import json
from typing import Iterable


def missing_logged_commits(candidate_hashes: list[str], logged_hashes: set[str]) -> list[str]:
    """One shared comparison for both commit_cost's and doc_metrics' jsonl -
    the candidate set differs (see md_touching_commits below) but "which of
    these hashes has no logged row" is the same question either way.
    """
    return [h for h in candidate_hashes if h not in logged_hashes]


def logged_keys(lines: Iterable[str], key: str = "commit_hash") -> set[str]:
    """Parses a ledger's jsonl lines (real JSON, never a text grep) and
    returns the set of `key` values already logged. Deliberately does no
    `.get()`/try-except swallowing: a line missing `key` raises `KeyError`
    and a malformed line raises `json.JSONDecodeError` - both loud, on
    purpose, so a jsonl schema change (renamed/reordered/reshaped column)
    surfaces as an obvious failure here instead of silently being read as
    "every commit is missing" or "every commit is logged".
    """
    keys = set()
    for line in lines:
        line = line.strip()
        if line:
            keys.add(json.loads(line)[key])
    return keys


def md_touching_commits(changed_files_by_commit: dict[str, list[str]]) -> list[str]:
    """doc_metrics logging's trigger condition is 'every commit touching a
    *.md file', not every commit - so its coverage check needs a narrower
    candidate set than commit_cost's (which triggers on every commit).
    """
    return [
        commit_hash for commit_hash, files in changed_files_by_commit.items()
        if any(f.endswith(".md") for f in files)
    ]


def hooks_path_configured(configured_value: str | None) -> bool:
    """`.githooks/pre-commit`'s app/tests and secrets-scan gates only run at
    all once `git config core.hooksPath .githooks` has been set - a purely
    local, per-clone setting git doesn't apply on its own (see
    SECRETS_SCAN.md / README.md's pre-commit hook section).
    """
    return configured_value == ".githooks"
