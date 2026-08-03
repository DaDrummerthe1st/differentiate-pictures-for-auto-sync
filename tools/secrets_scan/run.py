"""Mechanized secrets-in-diff scan, run from .githooks/pre-commit. See
../../documentation/tooling/SECRETS_SCAN.md.

Usage:
  python3 tools/secrets_scan/run.py             # scan the staged diff (git diff --cached)

Exits 1 (and prints every finding) if a high-confidence secret pattern
appears on an added line, or a non-template .env file is staged; 0 if
clean. Findings never print the full matched secret - only a redacted
prefix - so a real leak isn't compounded by putting it in a terminal/CI log.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scan import is_risky_env_filename, scan_diff  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

# This scanner's own test fixtures are deliberate secret-pattern lookalikes
# (see test_scan.py) - excluded here the same way redundancy_scan excludes
# its own known-repetitive files, rather than weakening the fixtures to
# dodge the very patterns they're testing.
_EXCLUDE_PATHSPEC = ":(exclude)tools/secrets_scan/test_scan.py"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def main() -> int:
    diff_text = _git("diff", "--cached", "-U0", "--no-color", "--", ".", _EXCLUDE_PATHSPEC)
    staged_files = [
        line for line in _git("diff", "--cached", "--name-only", "--", ".", _EXCLUDE_PATHSPEC).splitlines()
        if line
    ]

    findings = scan_diff(diff_text)
    risky_files = [f for f in staged_files if is_risky_env_filename(f)]

    if not findings and not risky_files:
        print("Secrets scan: clean.")
        return 0

    for finding in findings:
        print(f"SECRET: {finding.pattern_name} in {finding.file} ({finding.redacted_snippet})")
    for path in risky_files:
        print(f"SECRET: local-looking .env file staged: {path}")

    print(
        f"\n{len(findings) + len(risky_files)} finding(s) - remove the secret/file from the "
        "staged diff, or if this is a known-safe fixture value, adjust "
        "tools/secrets_scan/scan.py's patterns rather than committing anyway."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
