"""TDD tests for tools/wrapup_checklist/checks.py. Run with:
python3 -m unittest tools.wrapup_checklist.test_checks -v
(stdlib unittest only, matching tools/doc_metrics/test_metrics.py's convention.)
"""
import json
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


class LoggedKeysTests(unittest.TestCase):
    """Replaces the ad-hoc JSON parsing that used to live inline in run.py's
    _logged_hashes() - moved here so the "does this survive a ledger schema
    change" behavior is pinned down by a test, not incidental.
    """

    def test_returns_the_key_value_from_each_well_formed_line(self):
        lines = [
            json.dumps({"commit_hash": "aaa", "cost_usd": 0.1}),
            json.dumps({"commit_hash": "bbb", "cost_usd": 0.2}),
        ]
        self.assertEqual(checks.logged_keys(lines), {"aaa", "bbb"})

    def test_skips_blank_lines(self):
        lines = [json.dumps({"commit_hash": "aaa"}), "", "   "]
        self.assertEqual(checks.logged_keys(lines), {"aaa"})

    def test_supports_a_different_key_for_doc_metrics_style_rows(self):
        lines = [json.dumps({"commit_hash": "aaa", "file_path": "README.md"})]
        self.assertEqual(checks.logged_keys(lines, key="commit_hash"), {"aaa"})

    def test_a_row_missing_the_expected_key_raises_loudly(self):
        # A renamed/reshaped ledger column must fail loudly, never be
        # silently treated as "commit not logged" - that would report a
        # false coverage gap instead of surfacing the real schema change.
        lines = [json.dumps({"commit_sha": "aaa"})]  # key renamed
        with self.assertRaises(KeyError):
            checks.logged_keys(lines)

    def test_a_malformed_json_line_raises_loudly(self):
        lines = ["{not valid json"]
        with self.assertRaises(json.JSONDecodeError):
            checks.logged_keys(lines)


if __name__ == "__main__":
    unittest.main()
