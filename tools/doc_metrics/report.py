"""Trend report over logged *.md character counts. See README.md.

Usage: python3 tools/doc_metrics/report.py
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
        print(f"{'commit':<10} {'recorded_at':<21} {'chars':>8} {'delta':>8} {'~tokens':>8}")
        for commit_hash, recorded_at in commits:
            total = _total_for_commit(conn, commit_hash)
            delta = total - prev_total if prev_total is not None else total
            est_tokens = round(total / TOKEN_CHAR_RATIO)
            print(f"{commit_hash[:10]:<10} {recorded_at:<21} {total:>8} {delta:>+8} {est_tokens:>8}")
            prev_total = total
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=Path(__file__).parent / "metrics.db", type=Path)
    args = parser.parse_args()
    print_report(args.db)


if __name__ == "__main__":
    main()
