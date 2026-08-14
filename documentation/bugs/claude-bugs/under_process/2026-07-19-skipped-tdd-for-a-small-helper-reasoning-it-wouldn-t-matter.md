# Skipped TDD for a small helper, reasoning it wouldn't matter

See [README.md](../README.md) for what belongs here.

Status: **recurring, not structurally fixed** — reopened 2026-08-14 (see Recurrence #1 below); the 2026-07-16 rule-wording fix did not hold.

Backfilled 2026-07-19 from CLAUDE.md's own TDD bullet, which had been carrying this incident's full narrative inline since 2026-07-16 — a violation of the very "every lapse is its own file" rule this folder exists to enforce, caught while trimming CLAUDE.md's accumulated detail.

## What happened

During photo-server Phase 1, `app/audit.py`'s `log_audit_event` helper got written before its test — the "small enough not to matter" reasoning was used to skip the failing-test-first step CLAUDE.md's TDD rule otherwise required unconditionally. Disclosed in the moment, not hidden. A later, unrelated code-review pass over the same area then caught a real bug: `app/db.py`'s `get_db()` was silently dropping commits on an exception path.

## Why it happened

CLAUDE.md's TDD rule at the time carried a "where practical" qualifier, which left room to judge a helper "small enough" to skip test-first for — exactly the judgment call that led here.

## What changed

Dropped the "where practical" qualifier from CLAUDE.md's TDD rule entirely, 2026-07-16: no exceptions for "small" or "obvious" code, ever. Also established, from this incident specifically: reviewed-and-lucky isn't the same as tested — the code-review pass finding the `get_db()` bug afterward doesn't retroactively excuse having skipped the test for `log_audit_event`. Run the full test suite before every commit, even for changes that look unrelated or untestable, was adopted as a direct consequence — cheap insurance against regressions that aren't obvious from reading the diff.

## Recurrence #1 (2026-08-14)

### What happened

While building the invite-by-email feature in one long session, `server/app/invites.py`, the `POST /invites`/`POST /invites/{token}/accept` routes in `auth_routes.py`, and `server/app/mail.py` were all written implementation-first — tests (`test_invites.py`, the new `test_auth_routes.py` cases, `test_mail.py`) were added afterward and verified together in one `pytest` run, never watched failing first. In the same session, immediately before this, `backfill_missing_usernames()` (`server/app/db.py`) *was* done correctly test-first. Joakim asked directly: "Are you doing this as TDD while developing each detail?" — the honest check against actual tool-call order found the answer was no for three of the four pieces built.

### Why it happened

Different shape from the original 2026-07-19 incident - there was no active "this is small enough to skip" rationalization this time, just silent process drift: moving fast across several related pieces (schema, data-access functions, routes, a new module) in sequence, treating "write it, then test it, then run everything together" as the natural rhythm for a fast-moving multi-file feature, without re-checking against the actual rule at each individual function. The rule-wording fix from the original incident (removing the "where practical" qualifier) closed the *rationalization* path but did nothing to catch drift that isn't accompanied by any stated reasoning at all - there was no thought to catch.

### What changed

No new mechanical enforcement exists or is claimed here - `.githooks/pre-commit` (added after the 2026-07-26 sibling incident) only verifies tests **pass** before a commit; it cannot detect **order** - whether a given test existed and was run-to-fail before its implementation was written. That is a genuine, still-open enforcement gap, not something this entry fixes. Behavioral correction only, same limitation as the recurring AskUserQuestion bug (`2026-07-19-asked-inline-instead-of-using-askuserquestion-for-a-real-user-decision.md`): known to be insufficient on its own, since the rule was already known and still didn't hold. Documented honestly per Joakim's standing preference for the real mechanical-vs-judgment distinction rather than reassurance that this is "handled."
