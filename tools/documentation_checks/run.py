"""Mechanical subset of documentation/tooling/CLEANING.md's audit methodology.
See ../../documentation/tooling/DOCUMENTATION_CHECKS.md.

Usage:
  python3 tools/documentation_checks/run.py

Exits 1 if a broken link or a topic folder missing TODO.md is found (hard
fails — CLAUDE.md's layout rule is unambiguous about both). Exits 0 with a
warning if a code-dir README looks too long to be a stub (soft signal — the
size heuristic can false-positive, so it doesn't block on its own).

This does NOT replace a real CLEANING.md pass: reading every doc in full and
cross-checking claims against the actual code both still need a person (or
an AI session) doing real comprehension, not a script.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from checks import (  # noqa: E402
    find_broken_links,
    find_non_stub_code_readmes,
    find_topic_folders_missing_todo,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# documentation/ subfolders (relative to documentation/, forward-slash form)
# that are pure-reference or pure-archive — no ongoing backlog of their own,
# so CLAUDE.md's "topic folders get a mandatory TODO.md" rule doesn't apply.
# This is a judgment call a script can't make on its own; keep it reviewable
# here rather than baked into checks.py's logic.
EXEMPT_FROM_TODO = frozenset({
    "policies",       # pure reference (POLICY.md), no README.md anyway
    "bugs/solved",    # archive of resolved investigations, not open work
    "bugs/claude",    # archive of process-lapse write-ups, not open work
})

# Code directories that may carry a stub README.md pointing into
# documentation/, per CLAUDE.md's layout rule.
CODE_DIRS_WITH_STUB_READMES = [
    "server",
    "tools/commit_cost",
    "tools/doc_metrics",
    "tools/create_bug_report",
    "tools/documentation_checks",
    "tools/redundancy_scan",
]
STUB_MAX_CHARS = 400


def main() -> int:
    hard_fail = False

    broken = find_broken_links(REPO_ROOT)
    if broken:
        hard_fail = True
        print(f"BROKEN LINKS ({len(broken)}):")
        for b in broken:
            rel = b.source_file.relative_to(REPO_ROOT)
            print(f"  {rel}: [{b.target}] -> {b.resolved} MISSING")
    else:
        print("Dead-link sweep: clean.")

    missing_todo = find_topic_folders_missing_todo(REPO_ROOT, EXEMPT_FROM_TODO)
    if missing_todo:
        hard_fail = True
        print(f"TOPIC FOLDERS MISSING TODO.md ({len(missing_todo)}):")
        for p in missing_todo:
            print(f"  {p.relative_to(REPO_ROOT)}")
    else:
        print("Topic-folder TODO.md check: clean.")

    non_stub = find_non_stub_code_readmes(
        REPO_ROOT, CODE_DIRS_WITH_STUB_READMES, STUB_MAX_CHARS
    )
    if non_stub:
        print(
            f"WARNING: {len(non_stub)} code-dir README(s) longer than "
            f"{STUB_MAX_CHARS} chars — check they're still stubs, not real content:"
        )
        for p in non_stub:
            print(f"  {p.relative_to(REPO_ROOT)}")
    else:
        print("Code-dir stub-README size check: clean.")

    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
