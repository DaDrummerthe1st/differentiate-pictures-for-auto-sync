"""Regression guard for run.py's git-call scaling, run with:
python3 -m unittest tools.wrapup_checklist.test_run -v

The bug class this guards against: the two now-retired check_coverage.sh
shell scripts each shelled out to grep/git once *per commit*, which is
sub-quadratic-to-quadratic in commit count and was flagged as the exact
future-proofing failure this rebuild needed to avoid (see WRAPUP_CHECKLIST.md's
"Scaling" section). run.py instead reads the whole commit history with one
`git log` call and does the per-commit reasoning in Python. This test doesn't
benchmark a 10x-scale repo directly (none exists to test against) - it pins
the *call count* instead, so a future edit that reintroduces a per-commit
subprocess call fails immediately rather than only showing up as a slowdown
once the repo is actually much bigger.
"""
import unittest
from unittest.mock import patch

from tools.wrapup_checklist import run


def _completed(stdout: str):
    class _Result:
        def __init__(self, out):
            self.stdout = out

    return _Result(stdout)


class GitCallCountTests(unittest.TestCase):
    def test_all_commit_hashes_issues_exactly_one_git_call_regardless_of_history_size(self):
        # 5,000 simulated commits - stands in for a repo ~10x today's size.
        fake_log = "\n".join(f"{'a' * 39}{i}" for i in range(5000))
        with patch.object(run.subprocess, "run", return_value=_completed(fake_log)) as mock_run:
            hashes = run._all_commit_hashes()

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(len(hashes), 5000)

    def test_changed_files_by_commit_issues_exactly_one_git_call_regardless_of_history_size(self):
        fake_log = "\n".join(
            f"@@{'b' * 39}{i}\nREADME.md\napp/main.py" for i in range(5000)
        )
        with patch.object(run.subprocess, "run", return_value=_completed(fake_log)) as mock_run:
            changed = run._changed_files_by_commit()

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(len(changed), 5000)


class CheckCoverageCurrentHeadExclusionTests(unittest.TestCase):
    """Regression guard for the bug found live 2026-08-04: after
    .githooks/post-commit started deferring commit_cost's newest-commit
    row (see COMMIT_COST.md), --coverage-only mode (exclude_current_head=
    False, what pre-commit runs) briefly still flagged that expected gap
    as MISSING - which then blocked the hook's own next auto-commit
    attempt for doc_metrics, every single time. commit_cost's newest hash
    must be excluded in *both* modes now; doc_metrics only in
    exclude_current_head=True mode (session close), since it has no such
    structural lag - post-commit logs it immediately and correctly.
    """

    def _run_with(self, *, exclude_current_head, commit_cost_logged, doc_metrics_logged, md_touching=True):
        with patch.object(run, "_all_commit_hashes", return_value=["newest", "older"]), \
             patch.object(run, "_changed_files_by_commit", return_value={
                 "newest": (["README.md"] if md_touching else ["app/main.py"]), "older": ["README.md"],
             }), \
             patch.object(run, "_logged_keys_from_file", side_effect=lambda path, key="commit_hash": (
                 commit_cost_logged if path == run.COMMIT_COST_JSONL else doc_metrics_logged
             )):
            return run.check_coverage(exclude_current_head=exclude_current_head)

    def test_coverage_only_mode_does_not_flag_commit_costs_expected_newest_gap(self):
        ok = self._run_with(
            exclude_current_head=False, commit_cost_logged={"older"}, doc_metrics_logged={"newest", "older"},
        )
        self.assertTrue(ok)

    def test_coverage_only_mode_still_flags_a_real_older_commit_cost_gap(self):
        ok = self._run_with(
            exclude_current_head=False, commit_cost_logged=set(), doc_metrics_logged={"newest", "older"},
        )
        self.assertFalse(ok)

    def test_coverage_only_mode_still_requires_doc_metrics_current(self):
        # doc_metrics has no structural lag - unlike commit_cost, its
        # newest commit must already be logged in --coverage-only mode.
        ok = self._run_with(
            exclude_current_head=False, commit_cost_logged={"older"}, doc_metrics_logged={"older"},
        )
        self.assertFalse(ok)

    def test_full_mode_excludes_newest_commit_for_both_ledgers(self):
        ok = self._run_with(
            exclude_current_head=True, commit_cost_logged={"older"}, doc_metrics_logged={"older"},
        )
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
