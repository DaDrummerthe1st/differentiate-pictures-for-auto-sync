# Skipped TDD for a small helper, reasoning it wouldn't matter

See [README.md](README.md) for what belongs here.

Backfilled 2026-07-19 from CLAUDE.md's own TDD bullet, which had been carrying this incident's full narrative inline since 2026-07-16 — a violation of the very "every lapse is its own file" rule this folder exists to enforce, caught while trimming CLAUDE.md's accumulated detail.

## What happened

During photo-server Phase 1, `app/audit.py`'s `log_audit_event` helper got written before its test — the "small enough not to matter" reasoning was used to skip the failing-test-first step CLAUDE.md's TDD rule otherwise required unconditionally. Disclosed in the moment, not hidden. A later, unrelated code-review pass over the same area then caught a real bug: `app/db.py`'s `get_db()` was silently dropping commits on an exception path.

## Why it happened

CLAUDE.md's TDD rule at the time carried a "where practical" qualifier, which left room to judge a helper "small enough" to skip test-first for — exactly the judgment call that led here.

## What changed

Dropped the "where practical" qualifier from CLAUDE.md's TDD rule entirely, 2026-07-16: no exceptions for "small" or "obvious" code, ever. Also established, from this incident specifically: reviewed-and-lucky isn't the same as tested — the code-review pass finding the `get_db()` bug afterward doesn't retroactively excuse having skipped the test for `log_audit_event`. Run the full test suite before every commit, even for changes that look unrelated or untestable, was adopted as a direct consequence — cheap insurance against regressions that aren't obvious from reading the diff.
