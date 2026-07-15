"""Character-count metrics for *.md files — see README.md for methodology.

Character count = Unicode codepoints (len() of UTF-8-decoded text), not
bytes and not a locale-dependent `wc` count, so numbers are reproducible
and comparable across machines and over time.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileCount:
    file_path: str
    char_count: int


def char_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8"))


def discover_md_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))


def build_snapshot_from_pairs(pairs: list[tuple[str, str]]) -> list[FileCount]:
    return [FileCount(file_path=path, char_count=len(content)) for path, content in pairs]


def build_snapshot(root: Path) -> list[FileCount]:
    pairs = [
        (str(p.relative_to(root)), p.read_text(encoding="utf-8"))
        for p in discover_md_files(root)
    ]
    return build_snapshot_from_pairs(pairs)


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS doc_char_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TEXT NOT NULL,
            commit_hash TEXT NOT NULL,
            branch TEXT NOT NULL,
            file_path TEXT NOT NULL,
            char_count INTEGER NOT NULL,
            UNIQUE(commit_hash, file_path)
        )
        """
    )
    conn.commit()


def upsert_db(
    db_path: Path,
    snapshot: list[FileCount],
    commit_hash: str,
    branch: str,
    recorded_at: str,
) -> None:
    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)
        for item in snapshot:
            conn.execute(
                """
                INSERT INTO doc_char_counts
                    (recorded_at, commit_hash, branch, file_path, char_count)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(commit_hash, file_path) DO UPDATE SET
                    char_count = excluded.char_count,
                    recorded_at = excluded.recorded_at,
                    branch = excluded.branch
                """,
                (recorded_at, commit_hash, branch, item.file_path, item.char_count),
            )
        conn.commit()
    finally:
        conn.close()


def _jsonl_has_commit(jsonl_path: Path, commit_hash: str) -> bool:
    if not jsonl_path.exists():
        return False
    with jsonl_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and json.loads(line).get("commit") == commit_hash:
                return True
    return False


def append_jsonl(
    jsonl_path: Path,
    snapshot: list[FileCount],
    commit_hash: str,
    branch: str,
    recorded_at: str,
) -> None:
    with jsonl_path.open("a", encoding="utf-8") as fh:
        for item in snapshot:
            fh.write(
                json.dumps(
                    {
                        "ts": recorded_at,
                        "commit": commit_hash,
                        "branch": branch,
                        "file": item.file_path,
                        "chars": item.char_count,
                    }
                )
                + "\n"
            )


def persist_snapshot(
    snapshot: list[FileCount],
    db_path: Path,
    jsonl_path: Path,
    commit_hash: str,
    branch: str,
    recorded_at: str,
) -> list[FileCount]:
    upsert_db(db_path, snapshot, commit_hash, branch, recorded_at)
    if not _jsonl_has_commit(jsonl_path, commit_hash):
        append_jsonl(jsonl_path, snapshot, commit_hash, branch, recorded_at)
    return snapshot


def rebuild_db_from_jsonl(db_path: Path, jsonl_path: Path) -> None:
    """Recreate metrics.db from metrics.jsonl (the git-tracked source of truth)."""
    if db_path.exists():
        db_path.unlink()
    if not jsonl_path.exists():
        return
    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)
        with jsonl_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                conn.execute(
                    """
                    INSERT INTO doc_char_counts
                        (recorded_at, commit_hash, branch, file_path, char_count)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(commit_hash, file_path) DO UPDATE SET
                        char_count = excluded.char_count,
                        recorded_at = excluded.recorded_at,
                        branch = excluded.branch
                    """,
                    (row["ts"], row["commit"], row["branch"], row["file"], row["chars"]),
                )
        conn.commit()
    finally:
        conn.close()


def record_snapshot(
    root: Path,
    db_path: Path,
    jsonl_path: Path,
    commit_hash: str,
    branch: str,
    recorded_at: str,
) -> list[FileCount]:
    snapshot = build_snapshot(root)
    return persist_snapshot(snapshot, db_path, jsonl_path, commit_hash, branch, recorded_at)
