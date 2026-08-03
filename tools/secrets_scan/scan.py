"""Pure logic for the grep-based secrets-in-diff scan raised in
documentation/tooling/TODO.md (2026-07-28) - mechanizes the manual scan an
AI session used to run by hand before every commit. See
../../documentation/tooling/SECRETS_SCAN.md.

Only high-confidence, vendor-specific patterns are checked (cloud provider
key formats, private key headers, well-known token prefixes) - a generic
"password=" style heuristic was deliberately left out: this repo already
carries fixture values like docker-compose.yml's "local-dev-only" DB
password, and a low-confidence pattern would either miss real secrets in
the noise or train a session to reflexively bypass the hook.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_PATTERNS: tuple[tuple[str, re.Pattern], ...] = (
    ("AWS Access Key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]+")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("Stripe live key", re.compile(r"(sk|rk)_live_[0-9A-Za-z]{20,}")),
)

_ENV_ALLOWED_SUFFIXES = frozenset({".example", ".sample", ".template"})


@dataclass(frozen=True)
class SecretFinding:
    file: str
    pattern_name: str
    redacted_snippet: str


def _redact(secret: str) -> str:
    if len(secret) <= 4:
        return "*" * len(secret)
    return secret[:4] + "…" + "*" * 4


def scan_diff(diff_text: str) -> list[SecretFinding]:
    """Scans unified diff text (e.g. `git diff --cached`) for high-confidence
    secret patterns on *added* lines only - a matching pattern on a removed
    line is a secret leaving the diff, not entering it.
    """
    findings: list[SecretFinding] = []
    current_file = "(unknown)"
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            path = line[len("+++ "):].strip()
            current_file = path[2:] if path.startswith("b/") else path
            continue
        if line.startswith("---") or line.startswith("+++"):
            continue
        if not line.startswith("+"):
            continue
        content = line[1:]
        for name, pattern in _PATTERNS:
            match = pattern.search(content)
            if match:
                findings.append(SecretFinding(
                    file=current_file, pattern_name=name, redacted_snippet=_redact(match.group(0)),
                ))
    return findings


def is_risky_env_filename(path: str) -> bool:
    """True for a staged `.env`-style file that isn't a template/example -
    an actual local secrets file has no business being committed at all,
    regardless of its contents matching a known pattern.
    """
    name = path.rsplit("/", 1)[-1]
    if not name.startswith(".env"):
        return False
    suffix = name[len(".env"):]
    if suffix == "":
        return True
    return suffix not in _ENV_ALLOWED_SUFFIXES
