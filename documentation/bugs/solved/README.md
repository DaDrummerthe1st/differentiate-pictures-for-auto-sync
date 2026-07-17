# bugs/solved/

Where a [reports/](../reports/) investigation file goes once it's
actually resolved — not mitigated, not "probably fine now," genuinely
confirmed fixed. Moved here rather than deleted so the investigation
trail (what was tried, what worked) stays available for a similar bug
later.

**On move**: rename the file to append `-SOLVED` before `.md` (e.g.
`2026-07-17-thumbnail-oom-under-load.md` ->
`2026-07-17-thumbnail-oom-under-load-SOLVED.md`), keeping the original
`<date>-<slug>` prefix so it still sorts and greps the same way. Use
`tools/new_bug_report/mark_solved.sh <report-filename>` to do the
move+rename consistently rather than by hand. Also remove the
corresponding entry from [../TODO.md](../TODO.md) at the same time — a
solved bug shouldn't still show up in the untriaged list.
