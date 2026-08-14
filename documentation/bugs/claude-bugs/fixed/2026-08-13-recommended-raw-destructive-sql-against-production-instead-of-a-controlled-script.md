# Recommended raw destructive SQL against production instead of a controlled script

See [README.md](../README.md) for what belongs here.

## What happened

While root-causing `2026-08-13-upload-reports-finished-but-no-files-land-in-folder-or-appear-in-browser.md`, the session correctly diagnosed a stale `auth` container, then correctly asked Joakim to rebuild it himself (never executed directly - consistent with WORKFLOW.md's "hand it over, don't execute it directly" for database schema changes). But once the rebuild predictably surfaced the already-known `NOT NULL` migration failure (`server/app/db.py`'s comment and `DEPLOYMENT.md` §4 both already documented that `users` needed clearing first), the session just **copy-pasted `DEPLOYMENT.md`'s existing `DELETE FROM audit_log; DELETE FROM users;` one-liner as a ready-to-run block**, with the destructive/irreversible consequences (both real accounts deleted, both passwords rotated, all audit history wiped) noted only *after* the command, as a "heads up," not raised as a trade-off *before* handing it over. Joakim had to stop and redirect: build a real script instead of hand-writing SQL against production.

## Why it happened

The session treated "this exact command already exists in our own docs" as sufficient license to hand it over unquestioned, instead of applying WORKFLOW.md's own "Argue with evidence" rule to the doc's approach itself. `DEPLOYMENT.md` §4 encodes the same shortcut (raw `DELETE` instead of a non-destructive backfill of the existing NULL `username` values) - that doc having already normalized the risky pattern made it easier to reach for again without re-evaluating it, especially under the real pressure of `auth` being mid-outage. WORKFLOW.md's "Ask for constraints before high-blast-radius work" was also not applied here: the destructive command was handed over as the default path rather than pausing to ask whether Joakim would prefer a non-destructive alternative (a backfill script) before offering the delete-and-recreate route at all.

## What changed

- Filed this report and, in the same session, built a non-destructive backfill script (generates opaque usernames for existing NULL rows in place, no deletes) as the actual fix for the immediate outage, plus a proper account-management script per Joakim's request - see the upload bug doc and the session's chat log for details.
- Tightened `documentation/policies/WORKFLOW.md`'s "Ask for constraints before high-blast-radius work" line to explicitly cover this case: before handing over any destructive/irreversible database command against a production database - even one already written down in an existing doc - state the non-destructive alternative and its trade-off first, and let Joakim pick, rather than defaulting to whatever the doc already happens to say.
