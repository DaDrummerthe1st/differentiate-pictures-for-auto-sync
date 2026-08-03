"""Session wrap-up checklist, run as code instead of relying on a session
reading and remembering documentation/tooling/README.md's table correctly
every time. See ../../documentation/tooling/WRAPUP_CHECKLIST.md for exactly
which rows this covers and which it can't.

Usage:
  python3 tools/wrapup_checklist/run.py

Exit code 1 if a mechanical check found something outstanding; 0 otherwise.
The judgment-call reminders never affect the exit code - a script can raise
them, but only a person (or an AI session) can actually resolve them.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from checks import hooks_path_configured, md_touching_commits, missing_logged_commits  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_METRICS_JSONL = REPO_ROOT / "tools" / "doc_metrics" / "metrics.jsonl"
COMMIT_COST_JSONL = REPO_ROOT / "tools" / "commit_cost" / "commit_costs.jsonl"

# The judgment-call rows from README.md's wrap-up table that no script can
# resolve - either the trigger condition itself needs a person to notice
# ("did a manifest change" is checkable, but "docker build ran this
# session" isn't visible in git at all), or the check is a genuine
# open-ended read (loose ends, forward-effectiveness note). Printed every
# run, unconditionally - the point is that a session still has to look,
# not that this script decides for them.
JUDGMENT_CALL_REMINDERS = [
    "server/tests (container-based) - run it if this session touched server/ or app/ "
    "and it hasn't already run clean against this code (see TOOLCHAIN.md for the command).",
    "Changelog entry - add one if this session made a meaningful change.",
    "Lockfile/manifest consistency - check it if a manifest file changed this session.",
    "Docker hygiene (dangling/abandoned images) - check it if docker build/compose build ran this session.",
    "Doc-drift check (status lines/TODO/specs vs. code) - run it if code or docs changed this session.",
    "Wider sweep (stale deps, dead code, stale TODO/FIXME, security gaps) - scope it to files touched this session.",
    "Loose ends in the chat (unanswered questions, dropped threads, unresolved TBDs).",
    "Stale-TODO glance (items already resolved but still marked open).",
    "Forward-effectiveness note (one concrete note on what would make the next session cheaper).",
]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout


def _all_commit_hashes() -> list[str]:
    return [h for h in _git("log", "--pretty=%H").splitlines() if h]


def _changed_files_by_commit() -> dict[str, list[str]]:
    out = _git("log", "--name-only", "--pretty=format:@@%H")
    result: dict[str, list[str]] = {}
    current = None
    for line in out.splitlines():
        if line.startswith("@@"):
            current = line[2:]
            result[current] = []
        elif line.strip() and current is not None:
            result[current].append(line.strip())
    return result


def _logged_hashes(jsonl_path: Path, key: str = "commit_hash") -> set[str]:
    if not jsonl_path.exists():
        return set()
    hashes = set()
    with jsonl_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                hashes.add(json.loads(line)[key])
    return hashes


def _hooks_path() -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"], cwd=REPO_ROOT, capture_output=True, text=True,
    )
    value = result.stdout.strip()
    return value or None


def main() -> int:
    ok = True

    all_hashes = _all_commit_hashes()
    changed_by_commit = _changed_files_by_commit()

    print("MECHANICAL CHECKS")
    print("-----------------")

    missing_cost = missing_logged_commits(all_hashes, _logged_hashes(COMMIT_COST_JSONL))
    # The current HEAD commit is always "missing" mid-session - commit_cost
    # logging happens *after* committing, one commit behind (see
    # COMMIT_COST.md) - so it's excluded here, same as check_coverage.sh's
    # own documented one-expected-exception.
    missing_cost = [h for h in missing_cost if h != all_hashes[0]] if all_hashes else missing_cost
    if missing_cost:
        ok = False
        print(f"[MISSING] commit_cost: {len(missing_cost)} commit(s) with no logged row (run tools/commit_cost/log.py):")
        for h in missing_cost:
            print(f"  {h}")
    else:
        print("[OK] commit_cost: every commit (except the current HEAD, not yet logged) has a row.")

    md_commits = md_touching_commits(changed_by_commit)
    missing_docs = missing_logged_commits(md_commits, _logged_hashes(DOC_METRICS_JSONL))
    missing_docs = [h for h in missing_docs if not all_hashes or h != all_hashes[0]]
    if missing_docs:
        ok = False
        print(f"[MISSING] doc_metrics: {len(missing_docs)} *.md-touching commit(s) with no logged row (run tools/doc_metrics/log.py):")
        for h in missing_docs:
            print(f"  {h}")
    else:
        print("[OK] doc_metrics: every *.md-touching commit (except the current HEAD) has a row.")

    if hooks_path_configured(_hooks_path()):
        print("[OK] pre-commit hooks: core.hooksPath is set to .githooks (app/tests + secrets scan enforced).")
    else:
        ok = False
        print("[MISSING] pre-commit hooks: core.hooksPath is not '.githooks' - run: git config core.hooksPath .githooks")

    doc_checks = subprocess.run(
        ["python3", "tools/documentation_checks/run.py"], cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if doc_checks.returncode == 0:
        print("[OK] documentation_checks: dead-link sweep and topic-folder TODO.md presence both clean.")
    else:
        ok = False
        print("[MISSING] documentation_checks found issues - run: python3 tools/documentation_checks/run.py")
        print(doc_checks.stdout)

    print()
    print("JUDGMENT-CALL REMINDERS (no mechanical check - confirm manually)")
    print("------------------------------------------------------------------")
    for reminder in JUDGMENT_CALL_REMINDERS:
        print(f"- {reminder}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
