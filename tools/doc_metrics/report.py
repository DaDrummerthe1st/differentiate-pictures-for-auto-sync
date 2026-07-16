"""Trend report over logged *.md character counts. See ../../documentation/tooling/DOC_METRICS.md.

Usage:
  python3 tools/doc_metrics/report.py           # per-commit trend
  python3 tools/doc_metrics/report.py --by-task # cost summary grouped by --task label
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

TOKEN_CHAR_RATIO = 4  # rough approximation only — see README.md's "token cost" note


def _total_for_commit(conn: sqlite3.Connection, commit_hash: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(char_count), 0) FROM doc_char_counts WHERE commit_hash = ?",
        (commit_hash,),
    ).fetchone()
    return row[0]


def _task_for_commit(conn: sqlite3.Connection, commit_hash: str) -> str | None:
    row = conn.execute(
        """
        SELECT task FROM doc_char_counts
        WHERE commit_hash = ? AND task IS NOT NULL
        LIMIT 1
        """,
        (commit_hash,),
    ).fetchone()
    return row[0] if row else None


def _commits_oldest_first(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    rows = conn.execute(
        """
        SELECT commit_hash, MIN(recorded_at) AS first_seen
        FROM doc_char_counts
        GROUP BY commit_hash
        ORDER BY first_seen ASC
        """
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


def print_report(db_path: Path) -> None:
    if not db_path.exists():
        print(f"No database at {db_path} yet — run log.py first.")
        return
    conn = sqlite3.connect(db_path)
    try:
        commits = _commits_oldest_first(conn)
        if not commits:
            print("No metrics recorded yet.")
            return
        prev_total = None
        print(f"{'commit':<10} {'recorded_at':<21} {'chars':>8} {'delta':>8} {'~tokens':>8}  task")
        for commit_hash, recorded_at in commits:
            total = _total_for_commit(conn, commit_hash)
            delta = total - prev_total if prev_total is not None else total
            est_tokens = round(total / TOKEN_CHAR_RATIO)
            task = _task_for_commit(conn, commit_hash) or ""
            print(f"{commit_hash[:10]:<10} {recorded_at:<21} {total:>8} {delta:>+8} {est_tokens:>8}  {task}")
            prev_total = total
    finally:
        conn.close()


def print_task_report(db_path: Path) -> None:
    if not db_path.exists():
        print(f"No database at {db_path} yet — run log.py first.")
        return
    conn = sqlite3.connect(db_path)
    try:
        commits = _commits_oldest_first(conn)
        if not commits:
            print("No metrics recorded yet.")
            return
        prev_total = None
        deltas_by_task: dict[str, int] = {}
        for commit_hash, _ in commits:
            total = _total_for_commit(conn, commit_hash)
            delta = total - prev_total if prev_total is not None else total
            prev_total = total
            task = _task_for_commit(conn, commit_hash)
            if task is not None:
                deltas_by_task[task] = deltas_by_task.get(task, 0) + delta
        if not deltas_by_task:
            print("No commits tagged with --task yet.")
            return
        print(f"{'task':<40} {'chars':>10} {'~tokens':>8}")
        for task, chars in sorted(deltas_by_task.items(), key=lambda kv: kv[1], reverse=True):
            print(f"{task:<40} {chars:>10} {round(chars / TOKEN_CHAR_RATIO):>8}")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=Path(__file__).parent / "metrics.db", type=Path)
    parser.add_argument(
        "--by-task", action="store_true",
        help="show total char/token cost per --task label instead of the per-commit trend",
    )
    args = parser.parse_args()
    if args.by_task:
        print_task_report(args.db)
    else:
        print_report(args.db)


if __name__ == "__main__":
    main()
