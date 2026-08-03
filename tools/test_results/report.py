"""Test-run trend report. See ../../documentation/tooling/TEST_RESULTS.md.

Usage:
  python3 tools/test_results/report.py             # one line per logged run
  python3 tools/test_results/report.py --suite app  # filter to one suite
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

JSONL_PATH = Path(__file__).parent / "test_runs.jsonl"


def _load_rows(suite: str | None) -> list[dict]:
    if not JSONL_PATH.exists():
        return []
    rows = []
    with JSONL_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if suite is None or row["suite"] == suite:
                rows.append(row)
    return rows


def print_report(suite: str | None) -> None:
    rows = _load_rows(suite)
    if not rows:
        print(f"No data at {JSONL_PATH} yet - run log.py first.")
        return

    print(f"{'commit':<10} {'suite':<8} {'passed':>7} {'failed':>7} {'errors':>7} {'skipped':>8} {'time(s)':>8}  recorded_at")
    for row in rows:
        print(
            f"{row['commit_hash'][:9]:<10} {row['suite']:<8} {row['passed']:>7} {row['failed']:>7} "
            f"{row['errors']:>7} {row['skipped']:>8} {row['duration_seconds']:>8.2f}  {row['recorded_at']}"
        )

    total_failed = sum(r["failed"] + r["errors"] for r in rows)
    print()
    print(f"{len(rows)} run(s) logged, {total_failed} total failed/errored test-cases across all runs.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", default=None)
    args = parser.parse_args()
    print_report(args.suite)


if __name__ == "__main__":
    main()
