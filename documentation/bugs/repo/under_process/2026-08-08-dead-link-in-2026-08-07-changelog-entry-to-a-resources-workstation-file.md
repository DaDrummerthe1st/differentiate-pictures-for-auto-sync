# Dead link in 2026-08-07 changelog entry to a resources/workstation file

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

`tools/wrapup_checklist/run.py` (2026-08-08, this session's wrap-up) reported one broken link:

```
documentation/changelog/2026-08-07T15-34-26Z-recover-plan-files-from-workstation-repo-add-plansdirectory.md:
[../../../../resources/workstation/documentation/bugs/claude-bugs/fixed/2026-08-07-dpfas-plan-files-wrongly-committed-into-workstation-repo.md]
-> /home/joakim/code/resources/workstation/documentation/bugs/claude-bugs/fixed/2026-08-07-dpfas-plan-files-wrongly-committed-into-workstation-repo.md MISSING
```

Not caused by this session's work — pre-existing, first surfaced by today's wrap-up checklist run.
Unrelated to anything built this session (admin photo-source setting, upload feature, sqlite
concurrency fix).

## Investigation log

1. Not investigated yet - found during wrap-up, deliberately not chased down mid-session per this
   repo's "changelog immutability" rule (a committed changelog entry is never edited even for a
   cosmetic/link fix; this needs a bug report instead, which is this file).
2. The link points into a *different* repo (`~/code/resources/workstation/`), not this one - the
   target file may have been renamed/moved/deleted over there, or the cross-repo reference was wrong
   from the start.

## Leading theory (unconfirmed)

The referenced file was part of a bug-report cleanup in the `resources/workstation` repo (its own
`claude-bugs/fixed/` tree) - possibly renamed, or moved into an archive, after this changelog entry
linked to it on 2026-08-07.

## Next session should start with

Check whether `~/code/resources/workstation/documentation/bugs/claude-bugs/fixed/` has a
similarly-named file today (renamed?) or whether it's genuinely gone. This changelog entry's own text
can't be edited to fix the link (immutability rule) - if the target is confirmed permanently gone,
the resolution is just closing this bug report noting that a historical cross-repo link has gone
stale, which is accepted/expected for cross-repo references over time, not silently fixed.
