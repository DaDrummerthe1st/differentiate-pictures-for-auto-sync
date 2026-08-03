"""Pure logic for the mechanical subset of the session wrap-up checklist
(documentation/tooling/README.md's table) - raised in
documentation/tooling/TODO.md 2026-07-19: the checklist relied on a session
reading and remembering it correctly every time, the same failure mode
tools/commit_cost/check_coverage.sh was built to close for its own numbers
(three commits silently missing a logged row, see COMMIT_COST.md). See
../../documentation/tooling/WRAPUP_CHECKLIST.md for which rows this
actually covers - several of the table's checks are genuine judgment calls
that no script can make, and are surfaced as reminders, not pass/fail.
"""
from __future__ import annotations


def missing_logged_commits(candidate_hashes: list[str], logged_hashes: set[str]) -> list[str]:
    """Same shape as check_coverage.sh's own comparison, generalized so it
    can run against either commit_cost's or doc_metrics' jsonl.
    """
    return [h for h in candidate_hashes if h not in logged_hashes]


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
