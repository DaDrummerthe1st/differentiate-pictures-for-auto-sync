"""TDD tests for tools/secrets_scan/scan.py. Run with:
python3 -m unittest tools.secrets_scan.test_scan -v
(stdlib unittest only, matching tools/doc_metrics/test_metrics.py's convention.)
"""
import unittest

from tools.secrets_scan import scan


class ScanDiffTests(unittest.TestCase):
    def test_flags_an_aws_access_key_id_in_an_added_line(self):
        diff = (
            "diff --git a/config.py b/config.py\n"
            "--- a/config.py\n"
            "+++ b/config.py\n"
            "@@ -1,0 +1,1 @@\n"
            "+AWS_KEY = \"AKIAABCDEFGHIJKLMNOP\"\n"
        )
        findings = scan.scan_diff(diff)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].file, "config.py")
        self.assertEqual(findings[0].pattern_name, "AWS Access Key ID")

    def test_flags_a_private_key_block_header(self):
        diff = (
            "--- /dev/null\n"
            "+++ b/id_rsa\n"
            "@@ -0,0 +1,1 @@\n"
            "+-----BEGIN RSA PRIVATE KEY-----\n"
        )
        findings = scan.scan_diff(diff)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].pattern_name, "Private key block")

    def test_flags_a_github_personal_access_token(self):
        diff = (
            "--- a/.env\n"
            "+++ b/.env\n"
            "@@ -1,0 +1,1 @@\n"
            "+GH_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwx\n"
        )
        findings = scan.scan_diff(diff)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].pattern_name, "GitHub token")

    def test_ignores_removed_lines_reintroducing_a_key(self):
        # A key present only on a "-" (removed) line is leaving the diff,
        # not entering it - flagging it would block a commit that is
        # actively cleaning up a past leak.
        diff = (
            "--- a/config.py\n"
            "+++ b/config.py\n"
            "@@ -1,1 +1,0 @@\n"
            "-AWS_KEY = \"AKIAABCDEFGHIJKLMNOP\"\n"
        )
        findings = scan.scan_diff(diff)
        self.assertEqual(findings, [])

    def test_ignores_ordinary_added_lines(self):
        diff = (
            "--- a/README.md\n"
            "+++ b/README.md\n"
            "@@ -1,0 +1,1 @@\n"
            "+Just a normal added line of documentation text.\n"
        )
        findings = scan.scan_diff(diff)
        self.assertEqual(findings, [])

    def test_does_not_leak_the_full_secret_in_the_finding(self):
        diff = (
            "--- a/config.py\n"
            "+++ b/config.py\n"
            "@@ -1,0 +1,1 @@\n"
            "+AWS_KEY = \"AKIAABCDEFGHIJKLMNOP\"\n"
        )
        findings = scan.scan_diff(diff)
        self.assertNotIn("AKIAABCDEFGHIJKLMNOP", findings[0].redacted_snippet)
        self.assertTrue(findings[0].redacted_snippet.startswith("AKIA"))


class RiskyEnvFilenameTests(unittest.TestCase):
    def test_flags_a_plain_dotenv_file(self):
        self.assertTrue(scan.is_risky_env_filename(".env"))
        self.assertTrue(scan.is_risky_env_filename("server/.env"))

    def test_flags_a_dotenv_variant(self):
        self.assertTrue(scan.is_risky_env_filename(".env.production"))
        self.assertTrue(scan.is_risky_env_filename(".env.local"))

    def test_does_not_flag_an_env_example_file(self):
        self.assertFalse(scan.is_risky_env_filename(".env.example"))
        self.assertFalse(scan.is_risky_env_filename(".env.sample"))

    def test_does_not_flag_unrelated_files(self):
        self.assertFalse(scan.is_risky_env_filename("server/config.py"))
        self.assertFalse(scan.is_risky_env_filename("environment.py"))


if __name__ == "__main__":
    unittest.main()
