"""TDD tests for tools/doc_metrics/metrics.py. Run with:
python3 -m unittest tools.doc_metrics.test_metrics -v
(pytest isn't installed in this environment — stdlib unittest only.)
"""
import json
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))
import metrics  # noqa: E402


def _init_git_repo(root: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"], cwd=root, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _git_add(root: Path, *paths: str) -> None:
    subprocess.run(["git", "add", *paths], cwd=root, check=True)


class CharCountTests(unittest.TestCase):
    def test_counts_unicode_codepoints_not_bytes(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            # em dash is 3 bytes in UTF-8 but exactly 1 character
            path.write_text("a—b", encoding="utf-8")
            self.assertEqual(metrics.char_count(path), 3)


class DiscoverMdFilesTests(unittest.TestCase):
    def test_finds_only_git_tracked_markdown_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / "sub").mkdir()
            (root / "a.md").write_text("x")
            (root / "sub" / "b.md").write_text("y")
            (root / "ignore.txt").write_text("z")
            (root / "untracked.md").write_text("w")
            _git_add(root, "a.md", "sub/b.md", "ignore.txt")
            found = metrics.discover_md_files(root)
            self.assertEqual(sorted(p.name for p in found), ["a.md", "b.md"])

    def test_excludes_gitignored_vendored_files_like_venv(self):
        # regression test: discover_md_files used to be a raw filesystem
        # walk (root.rglob("*.md")), which picked up vendored *.md files
        # inside gitignored directories such as .venv — inflating char
        # counts with third-party license text that isn't this repo's
        # documentation and varies per machine/install.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / ".venv" / "pkg").mkdir(parents=True)
            (root / ".venv" / "pkg" / "LICENSE.md").write_text("vendored license")
            (root / "real.md").write_text("actual docs")
            _git_add(root, "real.md")
            found = metrics.discover_md_files(root)
            self.assertEqual(sorted(p.name for p in found), ["real.md"])


class BuildSnapshotFromPairsTests(unittest.TestCase):
    def test_computes_char_count_per_pair(self):
        snapshot = metrics.build_snapshot_from_pairs([("a.md", "hello"), ("b.md", "a—b")])
        self.assertEqual(
            snapshot,
            [metrics.FileCount("a.md", 5), metrics.FileCount("b.md", 3)],
        )


class RecordSnapshotTests(unittest.TestCase):
    def test_writes_one_db_row_and_one_jsonl_line_per_file(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _init_git_repo(root)
            (root / "a.md").write_text("hello")
            _git_add(root, "a.md")
            db_path = Path(tmp) / "metrics.db"
            jsonl_path = Path(tmp) / "metrics.jsonl"

            metrics.record_snapshot(
                root, db_path, jsonl_path, "abc123", "main", "2026-07-15T20:00:00+00:00"
            )

            conn = sqlite3.connect(db_path)
            rows = conn.execute(
                "SELECT file_path, char_count, commit_hash, branch FROM doc_char_counts"
            ).fetchall()
            conn.close()
            self.assertEqual(rows, [("a.md", 5, "abc123", "main")])

            lines = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["file"], "a.md")
            self.assertEqual(record["chars"], 5)
            self.assertEqual(record["commit"], "abc123")

    def test_task_is_stored_per_row_in_db_and_jsonl(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _init_git_repo(root)
            (root / "a.md").write_text("hello")
            _git_add(root, "a.md")
            db_path = Path(tmp) / "metrics.db"
            jsonl_path = Path(tmp) / "metrics.jsonl"

            metrics.record_snapshot(
                root, db_path, jsonl_path, "abc123", "main",
                "2026-07-15T20:00:00+00:00", task="photo-server TODO 0.3",
            )

            conn = sqlite3.connect(db_path)
            row = conn.execute(
                "SELECT task FROM doc_char_counts WHERE commit_hash = 'abc123'"
            ).fetchone()
            conn.close()
            self.assertEqual(row[0], "photo-server TODO 0.3")

            line = jsonl_path.read_text(encoding="utf-8").strip()
            record = json.loads(line)
            self.assertEqual(record["task"], "photo-server TODO 0.3")

    def test_task_defaults_to_null_when_not_given(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _init_git_repo(root)
            (root / "a.md").write_text("hello")
            _git_add(root, "a.md")
            db_path = Path(tmp) / "metrics.db"
            jsonl_path = Path(tmp) / "metrics.jsonl"

            metrics.record_snapshot(
                root, db_path, jsonl_path, "abc123", "main", "2026-07-15T20:00:00+00:00"
            )

            conn = sqlite3.connect(db_path)
            row = conn.execute(
                "SELECT task FROM doc_char_counts WHERE commit_hash = 'abc123'"
            ).fetchone()
            conn.close()
            self.assertIsNone(row[0])

            record = json.loads(jsonl_path.read_text(encoding="utf-8").strip())
            self.assertIsNone(record["task"])

    def test_rerunning_for_same_commit_does_not_duplicate_rows_or_lines(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _init_git_repo(root)
            (root / "a.md").write_text("hello")
            _git_add(root, "a.md")
            db_path = Path(tmp) / "metrics.db"
            jsonl_path = Path(tmp) / "metrics.jsonl"

            metrics.record_snapshot(
                root, db_path, jsonl_path, "abc123", "main", "2026-07-15T20:00:00+00:00"
            )
            metrics.record_snapshot(
                root, db_path, jsonl_path, "abc123", "main", "2026-07-15T20:05:00+00:00"
            )

            conn = sqlite3.connect(db_path)
            row_count = conn.execute("SELECT COUNT(*) FROM doc_char_counts").fetchone()[0]
            conn.close()
            self.assertEqual(row_count, 1)

            lines = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)

    def test_new_commit_adds_rows_without_removing_old_ones(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _init_git_repo(root)
            (root / "a.md").write_text("hello")
            _git_add(root, "a.md")
            db_path = Path(tmp) / "metrics.db"
            jsonl_path = Path(tmp) / "metrics.jsonl"

            metrics.record_snapshot(
                root, db_path, jsonl_path, "commit1", "main", "2026-07-15T20:00:00+00:00"
            )
            (root / "a.md").write_text("hello world")
            metrics.record_snapshot(
                root, db_path, jsonl_path, "commit2", "main", "2026-07-15T20:10:00+00:00"
            )

            conn = sqlite3.connect(db_path)
            rows = conn.execute(
                "SELECT commit_hash, char_count FROM doc_char_counts ORDER BY commit_hash"
            ).fetchall()
            conn.close()
            self.assertEqual(rows, [("commit1", 5), ("commit2", 11)])


class RebuildDbFromJsonlTests(unittest.TestCase):
    def test_rebuilds_db_rows_from_existing_jsonl(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            _init_git_repo(root)
            (root / "a.md").write_text("hello")
            _git_add(root, "a.md")
            db_path = Path(tmp) / "metrics.db"
            jsonl_path = Path(tmp) / "metrics.jsonl"
            metrics.record_snapshot(
                root, db_path, jsonl_path, "commit1", "main", "2026-07-15T20:00:00+00:00"
            )

            db_path.unlink()
            metrics.rebuild_db_from_jsonl(db_path, jsonl_path)

            conn = sqlite3.connect(db_path)
            rows = conn.execute(
                "SELECT file_path, char_count, commit_hash, branch FROM doc_char_counts"
            ).fetchall()
            conn.close()
            self.assertEqual(rows, [("a.md", 5, "commit1", "main")])


if __name__ == "__main__":
    unittest.main()
