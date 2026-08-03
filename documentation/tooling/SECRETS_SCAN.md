# secrets_scan

**Purpose:** mechanizes the manual secrets-in-diff scan an AI session used to run by hand before every commit — raised in [TODO.md](TODO.md) 2026-07-28, same self-enforcing rationale as `.githooks/pre-commit`'s existing `app/tests` gate: a rule that only lives in memory gets skipped eventually, a rule a hook enforces can't be.

## What it checks

`tools/secrets_scan/scan.py` inspects the **staged diff** (`git diff --cached`) for two things, on *added* lines only — a pattern on a removed line is a secret leaving the diff, not entering it:

1. **High-confidence vendor-specific patterns**: AWS access key IDs, private key block headers, GitHub/Slack tokens, Google API keys, Stripe live keys.
2. **A non-template `.env` file being staged** (`.env`, `.env.local`, `.env.production`, …) — `.env.example`/`.env.sample`/`.env.template` are exempt.

**Deliberately not checked**: a generic `password=`/`secret=` assignment heuristic. This repo already carries legitimate fixture values (`docker-compose.yml`'s `local-dev-only` DB password, `app/tests_selenium/conftest.py`'s test JWT secret) that a low-confidence pattern would either have to special-case one by one or flag every time, training a session to reflexively reach for `--no-verify`. High-confidence patterns only, same trade-off [POLICY.md](../policies/POLICY.md) already draws between a real credential and a disposable fixture value.

## Findings never contain the full secret

A match prints its pattern name, file, and a redacted snippet (`AKIA…****`) — never the matched string in full — so a real leak isn't compounded by putting it whole into a terminal or CI log.

## False positives

If a genuinely safe fixture value trips a pattern, the fix is to adjust `tools/secrets_scan/scan.py`'s patterns (or, for this tool's own test fixtures, the `tools/secrets_scan/test_scan.py` exclusion already wired into `run.py`) — not to reach for `--no-verify` on that commit and every one after it.

## Running it

```
python3 -m unittest tools.secrets_scan.test_scan -v   # tests
python3 tools/secrets_scan/run.py                       # scan the current staged diff
```

Wired into `.githooks/pre-commit`, right after the `app/tests` gate — blocks the commit on any finding. Not active until the one-time `git config core.hooksPath .githooks` setup (see [README.md](README.md)).
