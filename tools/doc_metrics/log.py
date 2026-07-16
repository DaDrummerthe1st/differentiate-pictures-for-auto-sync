"""Snapshot *.md character counts, tied to a git commit. See ../../documentation/tooling/DOC_METRICS.md.

Usage:
  python3 tools/doc_metrics/log.py                        # snapshot HEAD
  python3 tools/doc_metrics/log.py --task "photo-server 0.3"  # tag it with a task
  python3 tools/doc_metrics/log.py --backfill              # snapshot every commit in history
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from metrics import (  # noqa: E402
    build_snapshot_from_pairs,
    persist_snapshot,
    rebuild_db_from_jsonl,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(__file__).parent / "metrics.db"
JSONL_PATH = Path(__file__).parent / "metrics.jsonl"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def log_current_commit(task: str | None = None) -> None:
    commit_hash = _git("rev-parse", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    paths = _md_files_at_commit(commit_hash)
    pairs = [(p, _read_file_at_commit(commit_hash, p)) for p in paths]
    snapshot = build_snapshot_from_pairs(pairs)
    persist_snapshot(snapshot, DB_PATH, JSONL_PATH, commit_hash, branch, recorded_at, task)
    total = sum(f.char_count for f in snapshot)
    print(f"Recorded {len(snapshot)} files, {total} total characters, "
          f"at commit {commit_hash[:10]} ({branch})"
          + (f", task={task!r}." if task else "."))


def _commits_oldest_first() -> list[tuple[str, str]]:
    out = _git("log", "--reverse", "--pretty=%H|%cI")
    return [tuple(line.split("|", 1)) for line in out.splitlines() if line]


def _md_files_at_commit(commit_hash: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", commit_hash], cwd=REPO_ROOT, text=True
    )
    return [line for line in out.strip().splitlines() if line.endswith(".md")]


def _read_file_at_commit(commit_hash: str, file_path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{commit_hash}:{file_path}"], cwd=REPO_ROOT
    ).decode("utf-8")


def backfill() -> None:
    recorded = 0
    for commit_hash, committer_date in _commits_oldest_first():
        paths = _md_files_at_commit(commit_hash)
        pairs = [(p, _read_file_at_commit(commit_hash, p)) for p in paths]
        snapshot = build_snapshot_from_pairs(pairs)
        persist_snapshot(snapshot, DB_PATH, JSONL_PATH, commit_hash, "historical", committer_date)
        recorded += 1
    print(f"Backfilled {recorded} commits into {DB_PATH.name} / {JSONL_PATH.name}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backfill", action="store_true", help="snapshot every commit, not just HEAD")
    parser.add_argument(
        "--rebuild-db", action="store_true", help="rebuild metrics.db from the git-tracked metrics.jsonl"
    )
    parser.add_argument(
        "--task", default=None,
        help="label this snapshot with the TODO task/outcome it served, e.g. 'photo-server 0.3'",
    )
    args = parser.parse_args()
    if args.rebuild_db:
        rebuild_db_from_jsonl(DB_PATH, JSONL_PATH)
        print(f"Rebuilt {DB_PATH.name} from {JSONL_PATH.name}.")
    elif args.backfill:
        backfill()
    else:
        log_current_commit(args.task)


if __name__ == "__main__":
    main()
