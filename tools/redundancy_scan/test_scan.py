"""TDD tests for tools/redundancy_scan/scan.py. Run with:
python3 -m unittest tools.redundancy_scan.test_scan -v
(pytest isn't installed in this environment - stdlib unittest only,
matching tools/doc_metrics/test_metrics.py's convention.)
"""
import unittest

from tools.redundancy_scan import scan


class FindRepeatedPhrasesTests(unittest.TestCase):
    def test_flags_a_verbatim_phrase_shared_across_two_files(self):
        shared = "the quick brown fox jumps over the lazy dog again today"
        files = {
            "a.md": f"Intro. {shared}. More unique text in file a follows here.",
            "b.md": f"Different opening. {shared}. Unrelated closing in file b.",
        }
        matches = scan.find_repeated_phrases(files, min_words=10)
        self.assertEqual(len(matches), 1)
        self.assertIn("quick brown fox", matches[0].phrase)

    def test_does_not_flag_a_shared_phrase_below_the_threshold(self):
        files = {
            "a.md": "short shared words here and nothing else at all",
            "b.md": "short shared words here but otherwise unrelated content",
        }
        matches = scan.find_repeated_phrases(files, min_words=10)
        self.assertEqual(matches, [])

    def test_does_not_flag_unrelated_files(self):
        files = {
            "a.md": "Completely unique content about apples and oranges only.",
            "b.md": "Totally different subject matter involving trains and bridges.",
        }
        matches = scan.find_repeated_phrases(files, min_words=5)
        self.assertEqual(matches, [])

    def test_ignores_punctuation_differences_between_occurrences(self):
        files = {
            "a.md": "one two three four five six seven eight nine ten, done.",
            "b.md": "Prefix: one two three four five six seven eight nine ten!",
        }
        matches = scan.find_repeated_phrases(files, min_words=10)
        self.assertEqual(len(matches), 1)

    def test_reports_both_file_names_involved(self):
        shared = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
        files = {"x.md": shared, "y.md": shared}
        matches = scan.find_repeated_phrases(files, min_words=10)
        self.assertEqual({matches[0].file_a, matches[0].file_b}, {"x.md", "y.md"})

    def test_reports_a_long_repeated_block_once_not_as_overlapping_windows(self):
        # A 20-word repeated run at min_words=10 should be one match of
        # size 20, not ~10 overlapping 10-word matches - the whole point
        # of using difflib's maximal matching blocks over fixed windows.
        shared = " ".join(f"word{i}" for i in range(20))
        files = {"a.md": shared, "b.md": shared}
        matches = scan.find_repeated_phrases(files, min_words=10)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].word_count, 20)

    def test_case_sensitive_by_default(self):
        # Verbatim means verbatim - a case difference at a sentence
        # boundary is a real (if minor) textual difference, not noise to
        # collapse away.
        shared_lower = "one two three four five six seven eight nine ten"
        shared_upper = "One two three four five six seven eight nine ten"
        files = {"a.md": shared_lower, "b.md": shared_upper}
        matches = scan.find_repeated_phrases(files, min_words=10)
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
