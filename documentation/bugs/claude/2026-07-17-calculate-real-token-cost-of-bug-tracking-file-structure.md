# Calculate real token cost of bug-tracking file structure

Not a lapse — a task Joakim set for next session: verify with real
numbers, not the qualitative reasoning used today.

## Task

1. Was deleting `bugs/claude/LOG.md` (done 2026-07-17, no index kept,
   `ls` the directory instead) actually token-cheaper, measured, not
   assumed? Compare: cost of writing/updating an index entry per bug
   vs. cost of a future session listing + grepping filenames instead.
2. Same question extended to the one-file-per-bug structure itself
   (`bugs/reports/`, `bugs/claude/`) — many small files each cost a
   separate tool call to read; is that actually cheaper than fewer,
   larger consolidated files for how this repo actually gets used
   (occasional full sweeps vs. targeted single-bug lookups)? Today's
   qualitative answer ("modestly cheaper, mainly by avoiding stale-index
   rework") was not backed by real token counts.

## Next session should start with

Pull real numbers: token counts for a representative file read/write,
`ls`+`grep` cost for a directory of N files, and the actual cadence
this repo sees (how often is "list everything" vs. "read one specific
bug" the real access pattern) before concluding either structure is
"cheaper" in general.
