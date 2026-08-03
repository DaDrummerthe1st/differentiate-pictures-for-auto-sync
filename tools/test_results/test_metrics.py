"""TDD tests for tools/test_results/metrics.py. Run with:
python3 -m unittest tools.test_results.test_metrics -v
(stdlib unittest only, matching tools/doc_metrics/test_metrics.py's convention.)
"""
import unittest

from tools.test_results import metrics


def _junit_xml(tests=1, failures=0, errors=0, skipped=0, time="1.0"):
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        f'<testsuites name="pytest tests">'
        f'<testsuite name="pytest" errors="{errors}" failures="{failures}" '
        f'skipped="{skipped}" tests="{tests}" time="{time}" '
        f'timestamp="2026-08-03T00:00:00" hostname="x">'
        f'<testcase classname="a" name="b" time="0.1" />'
        f'</testsuite></testsuites>'
    )


class ParseJunitXmlTests(unittest.TestCase):
    def test_reads_counts_and_duration_from_a_single_testsuite(self):
        result = metrics.parse_junit_xml(_junit_xml(tests=58, failures=0, errors=0, skipped=0, time="1.121"))
        self.assertEqual(result.tests, 58)
        self.assertEqual(result.failures, 0)
        self.assertEqual(result.errors, 0)
        self.assertEqual(result.skipped, 0)
        self.assertAlmostEqual(result.duration_seconds, 1.121)

    def test_passed_is_derived_not_a_separate_junit_field(self):
        # junit xml has no explicit "passed" attribute - it's always
        # tests minus every other counted outcome.
        result = metrics.parse_junit_xml(_junit_xml(tests=10, failures=2, errors=1, skipped=1))
        self.assertEqual(result.passed, 6)

    def test_handles_a_bare_testsuite_root_without_the_testsuites_wrapper(self):
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<testsuite name="pytest" errors="0" failures="1" skipped="0" tests="3" time="0.5">'
            '</testsuite>'
        )
        result = metrics.parse_junit_xml(xml)
        self.assertEqual(result.tests, 3)
        self.assertEqual(result.failures, 1)
        self.assertEqual(result.passed, 2)

    def test_sums_across_multiple_testsuite_elements(self):
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<testsuites name="pytest tests">'
            '<testsuite name="a" errors="0" failures="1" skipped="0" tests="5" time="1.0"></testsuite>'
            '<testsuite name="b" errors="1" failures="0" skipped="2" tests="4" time="0.5"></testsuite>'
            '</testsuites>'
        )
        result = metrics.parse_junit_xml(xml)
        self.assertEqual(result.tests, 9)
        self.assertEqual(result.failures, 1)
        self.assertEqual(result.errors, 1)
        self.assertEqual(result.skipped, 2)
        self.assertAlmostEqual(result.duration_seconds, 1.5)
        self.assertEqual(result.passed, 5)

    def test_raises_on_xml_with_no_testsuite_at_all(self):
        with self.assertRaises(ValueError):
            metrics.parse_junit_xml('<?xml version="1.0"?><testsuites></testsuites>')


class BuildRowTests(unittest.TestCase):
    def test_row_carries_every_field_the_ledger_needs(self):
        result = metrics.TestRunResult(tests=10, failures=1, errors=0, skipped=2, duration_seconds=3.5)
        row = metrics.build_row(
            result, suite="app", commit_hash="abc123", recorded_at="2026-08-03T00:00:00+00:00", exit_code=1,
        )
        self.assertEqual(row["suite"], "app")
        self.assertEqual(row["commit_hash"], "abc123")
        self.assertEqual(row["recorded_at"], "2026-08-03T00:00:00+00:00")
        self.assertEqual(row["tests"], 10)
        self.assertEqual(row["passed"], 7)
        self.assertEqual(row["failed"], 1)
        self.assertEqual(row["errors"], 0)
        self.assertEqual(row["skipped"], 2)
        self.assertAlmostEqual(row["duration_seconds"], 3.5)
        self.assertEqual(row["exit_code"], 1)


if __name__ == "__main__":
    unittest.main()
