# bugs/TODO.md

No index is kept here — it proved unreliable (drifted out of sync
repeatedly; see `documentation/bugs/claude/` for the pattern). Browse
[reports/](reports/) directly: filenames are `<date>-<short-slug>.md`,
self-describing, and each file opens with a `Status:` line conveying
where it stands. `ls documentation/bugs/reports/` is the reliable way
to see what's open — cheaper and more accurate than a hand-maintained
list.

Use `tools/new_bug_report/new_bug_report.sh "Short bug title"` to create
one. Once genuinely resolved (not just mitigated), move it with
`tools/new_bug_report/mark_solved.sh <filename>` into
[solved/](solved/README.md).
