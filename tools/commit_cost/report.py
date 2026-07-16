"""Per-commit token/dollar cost report. See ../../documentation/tooling/COMMIT_COST.md.

Usage:
  python3 tools/commit_cost/report.py            # one line per commit
  python3 tools/commit_cost/report.py --by-session  # summed per session_id
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

JSONL_PATH = Path(__file__).parent / "commit_costs.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_rows() -> list[dict]:
    if not JSONL_PATH.exists():
        return []
    rows = []
    with JSONL_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _subject_for(commit_hash: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "show", "-s", "--format=%s", commit_hash], cwd=REPO_ROOT, text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "(unknown commit)"


def print_report() -> None:
    rows = _load_rows()
    if not rows:
        print(f"No data at {JSONL_PATH} yet — run log.py first.")
        return
    print(f"{'commit':<10} {'tokens':>10} {'cost_usd':>10}  subject")
    for row in rows:
        cost = row["cost_usd"]
        cost_str = f"{cost:.4f}" if cost is not None else "unknown"
        subject = _subject_for(row["commit_hash"])
        print(f"{row['commit_hash'][:9]:<10} {row['total_billed_tokens']:>10} {cost_str:>10}  {subject}")

    total_tokens = sum(r["total_billed_tokens"] for r in rows)
    total_cost = sum(r["cost_usd"] for r in rows if r["cost_usd"] is not None)
    human_only = sum(1 for r in rows if not r["llm_session_found"])
    print()
    print(f"Total: {total_tokens} tokens, ${total_cost:.4f} across {len(rows)} commits "
          f"({human_only} human-only, real 0 cost).")


def print_by_session() -> None:
    rows = _load_rows()
    if not rows:
        print(f"No data at {JSONL_PATH} yet — run log.py first.")
        return
    totals: dict[str, dict] = {}
    for row in rows:
        session_id = row["session_id"] or "(human, no session)"
        bucket = totals.setdefault(session_id, {"tokens": 0, "cost": 0.0, "commits": 0})
        bucket["tokens"] += row["total_billed_tokens"]
        if row["cost_usd"] is not None:
            bucket["cost"] += row["cost_usd"]
        bucket["commits"] += 1

    print(f"{'session_id':<38} {'commits':>7} {'tokens':>10} {'cost_usd':>10}")
    for session_id, bucket in sorted(totals.items(), key=lambda kv: kv[1]["cost"], reverse=True):
        print(f"{session_id:<38} {bucket['commits']:>7} {bucket['tokens']:>10} {bucket['cost']:>10.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--by-session", action="store_true")
    args = parser.parse_args()
    if args.by_session:
        print_by_session()
    else:
        print_report()


if __name__ == "__main__":
    main()
