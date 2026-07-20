"""Mechanized redundant-phrase scan for documentation/tooling/CLEANING.md's
"cross-reference before redundancy" step. See
../../documentation/tooling/REDUNDANCY_SCAN.md.

Usage:
  python3 tools/redundancy_scan/run.py [--min-words N]

Always exits 0 - unlike documentation_checks/run.py's dead-link/TODO.md
checks, a repeated phrase is never an unambiguous violation on its own
(templated boilerplate and deliberate standalone restatement both repeat
legitimately). This only surfaces candidates; a person still judges each
one, per CLEANING.md's "fix vs. flag" rule.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scan import find_repeated_phrases  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

# CHANGELOG.md is append-only and its dated entries share template
# boilerplate by design (see CLEANING.md) - excluding it here keeps the
# scan focused on prose that's actually a candidate for de-duplication.
EXCLUDED = frozenset({"CHANGELOG.md"})


def _tracked_md_files(root: Path) -> dict[str, str]:
    out = subprocess.run(
        ["git", "ls-files", "*.md"], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    files = {}
    for line in out.splitlines():
        if line in EXCLUDED:
            continue
        files[line] = (root / line).read_text(encoding="utf-8", errors="replace")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-words", type=int, default=10,
        help="minimum contiguous matching word count to report (default: 10)",
    )
    args = parser.parse_args()

    files = _tracked_md_files(REPO_ROOT)
    matches = find_repeated_phrases(files, min_words=args.min_words)
    if not matches:
        print(f"Redundancy scan: no repeated phrases found at >= {args.min_words} words.")
        return 0

    print(
        f"REPEATED PHRASES ({len(matches)}, >= {args.min_words} words) "
        "- candidates for review, not automatic fixes:"
    )
    for m in sorted(matches, key=lambda m: -m.word_count):
        print(f"\n[{m.word_count} words] {m.file_a}  <->  {m.file_b}")
        print(f'  "{m.phrase}"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
