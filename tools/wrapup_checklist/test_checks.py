"""TDD tests for tools/wrapup_checklist/checks.py. Run with:
python3 -m unittest tools.wrapup_checklist.test_checks -v
(stdlib unittest only, matching tools/doc_metrics/test_metrics.py's convention.)
"""
import unittest

from tools.wrapup_checklist import checks


class MissingLoggedCommitsTests(unittest.TestCase):
    def test_flags_a_candidate_commit_with_no_logged_row(self):
        result = checks.missing_logged_commits(
            candidate_hashes=["aaa", "bbb", "ccc"], logged_hashes={"aaa", "ccc"},
        )
        self.assertEqual(result, ["bbb"])

    def test_empty_when_every_candidate_is_logged(self):
        result = checks.missing_logged_commits(
            candidate_hashes=["aaa", "bbb"], logged_hashes={"aaa", "bbb", "zzz"},
        )
        self.assertEqual(result, [])

    def test_preserves_candidate_order(self):
        result = checks.missing_logged_commits(
            candidate_hashes=["ccc", "aaa", "bbb"], logged_hashes=set(),
        )
        self.assertEqual(result, ["ccc", "aaa", "bbb"])


class HooksPathConfiguredTests(unittest.TestCase):
    def test_true_when_set_to_the_repo_githooks_dir(self):
        self.assertTrue(checks.hooks_path_configured(".githooks"))

    def test_false_when_unset(self):
        self.assertFalse(checks.hooks_path_configured(None))

    def test_false_when_set_to_something_else(self):
        self.assertFalse(checks.hooks_path_configured(".git/hooks"))


class MdTouchingCommitsTests(unittest.TestCase):
    def test_flags_a_commit_whose_changed_files_include_a_markdown_file(self):
        result = checks.md_touching_commits({
            "aaa": ["app/main.py", "README.md"],
            "bbb": ["app/main.py"],
        })
        self.assertEqual(result, ["aaa"])

    def test_empty_when_no_commit_touches_markdown(self):
        result = checks.md_touching_commits({"aaa": ["app/main.py"]})
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
