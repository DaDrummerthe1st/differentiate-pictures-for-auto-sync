"""Run a pytest suite and append its result to the test-result ledger.
See ../../documentation/tooling/TEST_RESULTS.md.

Usage:
  python3 tools/test_results/log.py --suite app       # python3 -m pytest app/tests
  python3 tools/test_results/log.py --suite server     # uv run pytest tests, from server/

Always logs the run and exits with pytest's own exit code - a failing suite
is exactly as important to have in the ledger as a passing one.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from metrics import build_row, parse_junit_xml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
JSONL_PATH = Path(__file__).parent / "test_runs.jsonl"

# Matches documentation/photo-server/TOOLCHAIN.md's documented commands for
# each suite - this tool doesn't invent its own invocation. `server` runs
# the default (no db/redis container, no -m docker) suite; bring up
# server/scripts/test_db.sh / test_redis.sh yourself first if those tests
# are the ones you need covered this run.
SUITES: dict[str, dict] = {
    "app": {"cwd": REPO_ROOT, "cmd": ["python3", "-m", "pytest", "app/tests", "-q"]},
    "server": {"cwd": REPO_ROOT / "server", "cmd": ["uv", "run", "pytest", "tests", "-q"]},
}


def _commit_hash() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def run_suite(name: str) -> tuple[dict, int]:
    if name not in SUITES:
        raise ValueError(f"unknown suite {name!r} - choices: {sorted(SUITES)}")
    suite = SUITES[name]
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        junit_path = Path(tmp.name)
    try:
        completed = subprocess.run(
            [*suite["cmd"], f"--junitxml={junit_path}"], cwd=suite["cwd"],
        )
        result = parse_junit_xml(junit_path.read_text(encoding="utf-8"))
    finally:
        junit_path.unlink(missing_ok=True)

    row = build_row(
        result, suite=name, commit_hash=_commit_hash(), recorded_at=recorded_at,
        exit_code=completed.returncode,
    )
    return row, completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, choices=sorted(SUITES))
    args = parser.parse_args()

    row, exit_code = run_suite(args.suite)

    with JSONL_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")

    print(
        f"[{row['suite']}] {row['passed']} passed, {row['failed']} failed, "
        f"{row['errors']} errors, {row['skipped']} skipped in {row['duration_seconds']:.2f}s "
        f"- logged to {JSONL_PATH.relative_to(REPO_ROOT)}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
