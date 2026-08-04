"""TDD tests for tools/commit_cost/metrics.py. Run with:
python3 -m unittest tools.commit_cost.test_metrics -v
(pytest isn't installed in this environment — stdlib unittest only, same as doc_metrics.)
"""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# Qualified import, not a sys.path + bare "import metrics" hack — this repo
# has multiple tools/*/metrics.py modules sharing that bare name, which
# collide in sys.modules when both test suites load in one process (see
# CHANGELOG). The qualified form keeps them distinct.
from tools.commit_cost import metrics


def _usage(input_tokens=0, output_tokens=0, cache_5m=0, cache_1h=0, cache_read=0):
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_5m + cache_1h,
        "cache_creation": {
            "ephemeral_5m_input_tokens": cache_5m,
            "ephemeral_1h_input_tokens": cache_1h,
        },
        "cache_read_input_tokens": cache_read,
    }


def _assistant_row(uuid, content, usage=None, model="claude-sonnet-5", is_sidechain=False, session_id="sess-1"):
    message = {"model": model, "content": content}
    if usage is not None:
        message["usage"] = usage
    return {
        "type": "assistant", "uuid": uuid, "isSidechain": is_sidechain,
        "sessionId": session_id, "message": message,
    }


def _tool_result_row(tool_use_id, text):
    return {
        "type": "user",
        "message": {"content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": text}]},
    }


def _bash_tool_use(tool_id, command):
    return {"type": "tool_use", "id": tool_id, "name": "Bash", "input": {"command": command}}


class ParseUsageTests(unittest.TestCase):
    def test_extracts_all_components(self):
        message = {"usage": _usage(input_tokens=2, output_tokens=243, cache_5m=100, cache_1h=15687, cache_read=20625)}
        totals = metrics.parse_usage(message)
        self.assertEqual(
            totals,
            metrics.UsageTotals(
                input_tokens=2, output_tokens=243,
                cache_creation_5m_tokens=100, cache_creation_1h_tokens=15687,
                cache_read_tokens=20625,
            ),
        )

    def test_returns_none_without_usage_key(self):
        self.assertIsNone(metrics.parse_usage({"content": []}))

    def test_missing_cache_creation_breakdown_defaults_to_5m(self):
        # older/synthetic rows may lack the "cache_creation" breakdown sub-object
        message = {
            "usage": {
                "input_tokens": 5, "output_tokens": 10,
                "cache_creation_input_tokens": 40, "cache_read_input_tokens": 0,
            }
        }
        totals = metrics.parse_usage(message)
        self.assertEqual(totals.cache_creation_5m_tokens, 40)
        self.assertEqual(totals.cache_creation_1h_tokens, 0)


class UsageTotalsTests(unittest.TestCase):
    def test_add_combines_components(self):
        a = metrics.UsageTotals(1, 2, 3, 4, 5)
        b = metrics.UsageTotals(10, 20, 30, 40, 50)
        self.assertEqual(a.add(b), metrics.UsageTotals(11, 22, 33, 44, 55))

    def test_total_billed_tokens_sums_every_component(self):
        t = metrics.UsageTotals(1, 2, 3, 4, 5)
        self.assertEqual(t.total_billed_tokens(), 15)


class FindCommitBoundariesTests(unittest.TestCase):
    def test_finds_boundary_from_tool_use_and_matching_result(self):
        rows = [
            _assistant_row("a1", [_bash_tool_use("tu1", "git commit -m 'x'")], usage=_usage(input_tokens=1)),
            _tool_result_row("tu1", "[master abc1234] some message\n 1 file changed"),
        ]
        boundaries = metrics.find_commit_boundaries(rows)
        self.assertEqual(
            boundaries,
            [metrics.CommitBoundary(row_index=0, short_hash="abc1234", session_id="sess-1")],
        )

    def test_ignores_non_commit_bash_calls(self):
        rows = [
            _assistant_row("a1", [_bash_tool_use("tu1", "git status --short")], usage=_usage(input_tokens=1)),
            _tool_result_row("tu1", "nothing to commit, working tree clean"),
        ]
        self.assertEqual(metrics.find_commit_boundaries(rows), [])

    def test_multiple_commits_produce_ordered_boundaries(self):
        rows = [
            _assistant_row("a1", [_bash_tool_use("tu1", "git commit -m a")], usage=_usage(input_tokens=1)),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
            _assistant_row("a2", [_bash_tool_use("tu2", "git commit -m b")], usage=_usage(input_tokens=1)),
            _tool_result_row("tu2", "[master bbb2222] B\n 1 file changed"),
        ]
        boundaries = metrics.find_commit_boundaries(rows)
        self.assertEqual(
            boundaries,
            [
                metrics.CommitBoundary(row_index=0, short_hash="aaa1111", session_id="sess-1"),
                metrics.CommitBoundary(row_index=2, short_hash="bbb2222", session_id="sess-1"),
            ],
        )

    def test_a_hook_triggered_nested_commit_does_not_shadow_the_outer_one(self):
        # .githooks/post-commit runs `git commit` again from *inside* the
        # Bash tool call that made the outer commit - git only prints the
        # outer commit's own "[branch hash]" confirmation line after all of
        # its hooks (including that nested commit) finish, so the nested
        # commit's line appears FIRST in the combined tool_result text, the
        # outer/real one LAST. Taking the first match (as a naive .search()
        # would) misattributes this turn's entire real usage to the free,
        # auto-generated nested commit instead of the real one that
        # produced it - found for real 2026-08-04 (18f8b64 vs. 31122a9).
        rows = [
            _assistant_row("a1", [_bash_tool_use("tu1", "git commit -m outer")], usage=_usage(input_tokens=42)),
            _tool_result_row(
                "tu1",
                "[pre-commit] ok\n[post-commit] logging...\n"
                "[master aaa1111] Log doc metrics and commit cost for the previous commit\n"
                "[post-commit] pushing...\n"
                "[master bbb2222] outer commit message\n 1 file changed",
            ),
        ]
        boundaries = metrics.find_commit_boundaries(rows)
        self.assertEqual(
            boundaries,
            [metrics.CommitBoundary(row_index=0, short_hash="bbb2222", session_id="sess-1")],
        )

    def test_two_commit_tool_uses_in_same_turn_both_recorded_at_that_row(self):
        rows = [
            _assistant_row(
                "a1",
                [_bash_tool_use("tu1", "git commit -m a"), _bash_tool_use("tu2", "git commit -m b")],
                usage=_usage(input_tokens=1),
            ),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
            _tool_result_row("tu2", "[master bbb2222] B\n 1 file changed"),
        ]
        boundaries = metrics.find_commit_boundaries(rows)
        self.assertEqual(
            boundaries,
            [
                metrics.CommitBoundary(row_index=0, short_hash="aaa1111", session_id="sess-1"),
                metrics.CommitBoundary(row_index=0, short_hash="bbb2222", session_id="sess-1"),
            ],
        )


class GroupEventsByCommitTests(unittest.TestCase):
    def test_attributes_usage_since_previous_boundary(self):
        rows = [
            _assistant_row("a0", [{"type": "text", "text": "thinking"}], usage=_usage(input_tokens=100)),
            _assistant_row("a1", [_bash_tool_use("tu1", "git commit -m a")], usage=_usage(input_tokens=1)),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
            _assistant_row("a2", [{"type": "text", "text": "more work"}], usage=_usage(input_tokens=50)),
            _assistant_row("a3", [_bash_tool_use("tu2", "git commit -m b")], usage=_usage(input_tokens=2)),
            _tool_result_row("tu2", "[master bbb2222] B\n 1 file changed"),
        ]
        commits = metrics.group_events_by_commit(rows)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].short_hash, "aaa1111")
        self.assertEqual(commits[0].usage.input_tokens, 101)  # rows a0 + a1
        self.assertEqual(commits[0].session_id, "sess-1")
        self.assertEqual(commits[1].short_hash, "bbb2222")
        self.assertEqual(commits[1].usage.input_tokens, 52)  # rows a2 + a3
        self.assertEqual(commits[1].session_id, "sess-1")

    def test_session_id_taken_from_the_boundary_row_itself(self):
        # a commit made in a resumed session: session_id reflects whichever
        # session actually issued the git commit, not an earlier one
        rows = [
            _assistant_row("a0", [{"type": "text", "text": "..."}], usage=_usage(input_tokens=10), session_id="sess-A"),
            _assistant_row(
                "a1", [_bash_tool_use("tu1", "git commit -m a")], usage=_usage(input_tokens=1), session_id="sess-B",
            ),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
        ]
        commits = metrics.group_events_by_commit(rows)
        self.assertEqual(commits[0].session_id, "sess-B")

    def test_same_row_double_boundary_yields_zero_usage_second_commit(self):
        rows = [
            _assistant_row(
                "a1",
                [_bash_tool_use("tu1", "git commit -m a"), _bash_tool_use("tu2", "git commit -m b")],
                usage=_usage(input_tokens=10),
            ),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
            _tool_result_row("tu2", "[master bbb2222] B\n 1 file changed"),
        ]
        commits = metrics.group_events_by_commit(rows)
        self.assertEqual(commits[0].usage.input_tokens, 10)
        self.assertEqual(commits[1].usage, metrics.UsageTotals(0, 0, 0, 0, 0))

    def test_sidechain_usage_is_included(self):
        rows = [
            _assistant_row("a0", [{"type": "text", "text": "delegate"}], usage=_usage(input_tokens=5), is_sidechain=True),
            _assistant_row("a1", [_bash_tool_use("tu1", "git commit -m a")], usage=_usage(input_tokens=1)),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
        ]
        commits = metrics.group_events_by_commit(rows)
        self.assertEqual(commits[0].usage.input_tokens, 6)

    def test_synthetic_model_rows_do_not_count_as_a_second_model(self):
        # Claude Code inserts zero-usage "<synthetic>" rows (observed after
        # compaction). They must not block single-model pricing eligibility.
        rows = [
            _assistant_row("a0", [{"type": "text", "text": "..."}], usage=_usage(input_tokens=5), model="claude-sonnet-5"),
            _assistant_row("a1", [{"type": "text", "text": "..."}], usage=_usage(), model="<synthetic>"),
            _assistant_row("a2", [_bash_tool_use("tu1", "git commit -m a")], usage=_usage(input_tokens=1), model="claude-sonnet-5"),
            _tool_result_row("tu1", "[master aaa1111] A\n 1 file changed"),
        ]
        commits = metrics.group_events_by_commit(rows)
        self.assertEqual(commits[0].models, ("claude-sonnet-5",))

    def test_no_commits_yields_no_entries(self):
        rows = [_assistant_row("a0", [{"type": "text", "text": "just chatting"}], usage=_usage(input_tokens=5))]
        self.assertEqual(metrics.group_events_by_commit(rows), [])


class CostTests(unittest.TestCase):
    def test_cost_applies_input_and_output_price(self):
        totals = metrics.UsageTotals(input_tokens=1_000_000, output_tokens=1_000_000,
                                      cache_creation_5m_tokens=0, cache_creation_1h_tokens=0, cache_read_tokens=0)
        pricing = {"claude-sonnet-5": metrics.ModelPricing(input_per_mtok=3.0, output_per_mtok=15.0)}
        self.assertAlmostEqual(metrics.compute_cost(totals, "claude-sonnet-5", pricing), 18.0)

    def test_cost_applies_cache_multipliers(self):
        totals = metrics.UsageTotals(
            input_tokens=0, output_tokens=0,
            cache_creation_5m_tokens=1_000_000, cache_creation_1h_tokens=1_000_000,
            cache_read_tokens=1_000_000,
        )
        pricing = {"claude-sonnet-5": metrics.ModelPricing(input_per_mtok=10.0, output_per_mtok=50.0)}
        # 5m write = 1.25x input, 1h write = 2x input, read = 0.1x input
        expected = 10.0 * 1.25 + 10.0 * 2.0 + 10.0 * 0.1
        self.assertAlmostEqual(metrics.compute_cost(totals, "claude-sonnet-5", pricing), expected)

    def test_unknown_model_raises(self):
        totals = metrics.UsageTotals(1, 1, 0, 0, 0)
        with self.assertRaises(KeyError):
            metrics.compute_cost(totals, "claude-nonexistent", pricing={})


class CandidatesForLoggingTests(unittest.TestCase):
    def test_without_exclude_head_includes_every_unlogged_hash(self):
        result = metrics.candidates_for_logging(
            all_hashes=["ccc", "bbb", "aaa"], already_logged={"aaa"}, exclude_head=False,
        )
        self.assertEqual(result, ["ccc", "bbb"])

    def test_exclude_head_drops_the_newest_hash_even_if_unlogged(self):
        # .githooks/post-commit's use case: HEAD is the commit that just
        # triggered this very hook run, from inside the same Bash tool
        # call - its git-commit tool_result hasn't been written to the
        # live transcript yet, so resolving it now would misread "no
        # session found (yet)" as "genuinely human" and log a false,
        # permanent 0 (see documentation/tooling/COMMIT_COST.md).
        result = metrics.candidates_for_logging(
            all_hashes=["ccc", "bbb", "aaa"], already_logged={"aaa"}, exclude_head=True,
        )
        self.assertEqual(result, ["bbb"])

    def test_exclude_head_is_a_no_op_when_head_is_already_logged(self):
        # Only ever drop the literal newest hash - never an older unlogged
        # one that happens to be first in the *candidate* list.
        result = metrics.candidates_for_logging(
            all_hashes=["ccc", "bbb", "aaa"], already_logged={"ccc"}, exclude_head=True,
        )
        self.assertEqual(result, ["bbb", "aaa"])

    def test_exclude_head_on_empty_history_does_not_crash(self):
        result = metrics.candidates_for_logging(all_hashes=[], already_logged=set(), exclude_head=True)
        self.assertEqual(result, [])


class IterTranscriptRowsTests(unittest.TestCase):
    def test_skips_blank_lines(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            path.write_text('{"a": 1}\n\n{"a": 2}\n')
            rows = list(metrics.iter_transcript_rows(path))
            self.assertEqual(rows, [{"a": 1}, {"a": 2}])


if __name__ == "__main__":
    unittest.main()
