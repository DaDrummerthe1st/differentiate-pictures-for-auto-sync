"""Pure logic for the per-run test-result ledger raised in
documentation/tooling/TODO.md (2026-07-18) - same append-only jsonl shape
as tools/doc_metrics/tools/commit_cost, but tracking pytest pass/fail/skip
counts and duration over time instead of doc size or token cost. See
../../documentation/tooling/TEST_RESULTS.md.

Reads pytest's own built-in `--junitxml` output - no plugin required, and
no re-parsing of `-q` terminal output whose format isn't a stable contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree


@dataclass(frozen=True)
class TestRunResult:
    tests: int
    failures: int
    errors: int
    skipped: int
    duration_seconds: float

    @property
    def passed(self) -> int:
        return self.tests - self.failures - self.errors - self.skipped


def parse_junit_xml(xml_text: str) -> TestRunResult:
    """Sums every <testsuite> element found - pytest emits one per run in
    the common case, wrapped in a <testsuites> root, but nothing here
    assumes there's exactly one.
    """
    root = ElementTree.fromstring(xml_text)
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    if not suites:
        raise ValueError("no <testsuite> element found in junit xml")

    tests = failures = errors = skipped = 0
    duration_seconds = 0.0
    for suite in suites:
        tests += int(suite.get("tests", 0))
        failures += int(suite.get("failures", 0))
        errors += int(suite.get("errors", 0))
        skipped += int(suite.get("skipped", 0))
        duration_seconds += float(suite.get("time", 0.0))

    return TestRunResult(
        tests=tests, failures=failures, errors=errors, skipped=skipped, duration_seconds=duration_seconds,
    )


def build_row(result: TestRunResult, *, suite: str, commit_hash: str, recorded_at: str, exit_code: int) -> dict:
    return {
        "suite": suite,
        "commit_hash": commit_hash,
        "recorded_at": recorded_at,
        "tests": result.tests,
        "passed": result.passed,
        "failed": result.failures,
        "errors": result.errors,
        "skipped": result.skipped,
        "duration_seconds": result.duration_seconds,
        "exit_code": exit_code,
    }
