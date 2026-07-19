"""TDD tests for tools/documentation_checks/checks.py. Run with:
python3 -m unittest tools.documentation_checks.test_checks -v
(pytest isn't installed in this environment — stdlib unittest only,
matching tools/doc_metrics/test_metrics.py's convention.)
"""
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.documentation_checks import checks


def _init_git_repo(root: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"], cwd=root, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _git_add(root: Path, *paths: str) -> None:
    subprocess.run(["git", "add", *paths], cwd=root, check=True)


class FindBrokenLinksTests(unittest.TestCase):
    def test_flags_a_relative_link_to_a_missing_file(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / "a.md").write_text("See [gone](missing.md) for detail.")
            _git_add(root, "a.md")
            broken = checks.find_broken_links(root)
            self.assertEqual(len(broken), 1)
            self.assertEqual(broken[0].target, "missing.md")

    def test_does_not_flag_a_link_that_resolves(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / "b.md").write_text("ok")
            (root / "a.md").write_text("See [b](b.md) for detail.")
            _git_add(root, "a.md", "b.md")
            broken = checks.find_broken_links(root)
            self.assertEqual(broken, [])

    def test_ignores_http_and_mailto_links(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / "a.md").write_text(
                "[web](https://example.com/x) and [mail](mailto:a@b.com)"
            )
            _git_add(root, "a.md")
            broken = checks.find_broken_links(root)
            self.assertEqual(broken, [])

    def test_resolves_a_link_with_an_anchor_fragment(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / "b.md").write_text("ok")
            (root / "a.md").write_text("See [b](b.md#section) for detail.")
            _git_add(root, "a.md", "b.md")
            broken = checks.find_broken_links(root)
            self.assertEqual(broken, [])

    def test_ignores_untracked_md_files(self):
        # matches doc_metrics' own git-ls-files scoping — an untracked
        # scratch file with a broken link shouldn't fail the check.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            (root / "untracked.md").write_text("[gone](missing.md)")
            broken = checks.find_broken_links(root)
            self.assertEqual(broken, [])


class FindTopicFoldersMissingTodoTests(unittest.TestCase):
    def test_flags_a_readme_only_folder_as_missing_todo(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "documentation" / "widgets"
            doc.mkdir(parents=True)
            (doc / "README.md").write_text("widgets")
            missing = checks.find_topic_folders_missing_todo(root, exempt=frozenset())
            self.assertEqual([p.name for p in missing], ["widgets"])

    def test_does_not_flag_a_folder_with_both_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "documentation" / "widgets"
            doc.mkdir(parents=True)
            (doc / "README.md").write_text("widgets")
            (doc / "TODO.md").write_text("nothing planned")
            missing = checks.find_topic_folders_missing_todo(root, exempt=frozenset())
            self.assertEqual(missing, [])

    def test_does_not_flag_an_exempt_folder(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "documentation" / "policies"
            doc.mkdir(parents=True)
            (doc / "README.md").write_text("policy folder, no README normally, but test anyway")
            missing = checks.find_topic_folders_missing_todo(root, exempt=frozenset({"policies"}))
            self.assertEqual(missing, [])

    def test_ignores_a_folder_with_no_readme_at_all(self):
        # e.g. a folder that's just scratch/generated, not a documented topic
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "documentation" / "stray"
            doc.mkdir(parents=True)
            (doc / "notes.txt").write_text("x")
            missing = checks.find_topic_folders_missing_todo(root, exempt=frozenset())
            self.assertEqual(missing, [])


class FindNonStubCodeReadmesTests(unittest.TestCase):
    def test_flags_a_readme_over_the_size_threshold(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "server").mkdir()
            (root / "server" / "README.md").write_text("x" * 500)
            flagged = checks.find_non_stub_code_readmes(root, ["server"], max_chars=400)
            self.assertEqual([p.parent.name for p in flagged], ["server"])

    def test_does_not_flag_a_short_stub(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "server").mkdir()
            (root / "server" / "README.md").write_text("Moved to documentation/. See there.")
            flagged = checks.find_non_stub_code_readmes(root, ["server"], max_chars=400)
            self.assertEqual(flagged, [])

    def test_does_not_flag_a_code_dir_with_no_readme(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app").mkdir()
            flagged = checks.find_non_stub_code_readmes(root, ["app"], max_chars=400)
            self.assertEqual(flagged, [])


if __name__ == "__main__":
    unittest.main()
