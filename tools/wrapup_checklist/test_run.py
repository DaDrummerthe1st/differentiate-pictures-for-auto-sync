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


if __name__ == "__main__":
    unittest.main()
