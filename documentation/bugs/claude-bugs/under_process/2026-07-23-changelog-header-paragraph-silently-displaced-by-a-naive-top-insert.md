# CHANGELOG header paragraph silently displaced by a naive top-insert

See [README.md](../README.md) for what belongs here.

## What happened

Merging `master` into `mamma-photo-viewer` (2026-07-23) produced a `CHANGELOG.md` with two problems, neither flagged as a conflict by `git merge`:

1. Entries landed out of "newest first" order — `master`'s block (up through 2026-07-23T11:08:19) sat above `mamma-photo-viewer`'s block (up through 2026-07-23T14:23:36, chronologically newer).
2. The file's own explanatory header paragraph ("One entry per revision, newest first. This file merges two changelog histories...") was missing from the top entirely — found later at line 61, stranded mid-file, immediately after one specific entry.

Traced with `git show <commit>:CHANGELOG.md` and `git log -S` across both branches' history:

- At the true merge-base (`89fbafc6`, 2026-07-21T04:54 CEST), the paragraph was correctly placed at the top on **both** branches.
- On `master`'s line, the very next commit touching the file — `cefdf78` ("Vendor jQuery, Bootstrap, and Material Symbols into the photo-viewer frontend", 2026-07-21T15:48 CEST, originally on branch `design/icons-and-ui-libs`, later fast-forwarded into `master`) — inserted its new entry directly under the `# Changelog` heading, pushing the paragraph down one slot instead of inserting below it. Confirmed via `git show cefdf78:CHANGELOG.md | sed -n '3p'`: line 3 is `cefdf78`'s own new entry heading, not the paragraph.
- Every later `master`-line commit then stacked its own entry above that already-buried paragraph (normal top-insertion), so it kept drifting deeper — 6 more commits, ending at line 61 by the time this merge happened.
- On the `mamma-photo-viewer` line, this exact same defect was present too (both branches share the identical state at `89fbafc6`... no — checked again: `89fbafc6` already had it correct, so the defect must have been introduced and then fixed even earlier, before `89fbafc6`, by commit `9d0a099`, which is why `mamma-photo-viewer`'s copy was clean by the time `89fbafc6` was cut). Either way: one line silently self-corrected within a commit or two; the other carried the defect for 2 days across 7 commits, undetected.
- Nothing (script or human review) checks `CHANGELOG.md`'s structural invariants (header paragraph present at top; entries in descending timestamp order) — a normal `git diff`/PR review of a single commit only ever sees the new entry being added correctly at whatever position the previous tip already had it, never the cumulative drift.

## Why it happened

Whatever process (AI session or otherwise) authored `cefdf78`'s `CHANGELOG.md` edit used a simple "insert my new entry right after the H1 heading" pattern without checking whether that slot already held a structural paragraph rather than another dated entry. A one-off mechanical slip at insertion time, silently self-perpetuating afterward since every subsequent top-insert just stacks correctly *relative to the already-wrong position*, never re-checking the file's actual invariants.

## What changed

- Fixed in the 2026-07-23 merge commit: `CHANGELOG.md` restructured — header paragraph restored to the true top, extended with one sentence documenting this second branch-divergence-and-remerge (mirroring the existing sentence for the first, 2026-07-21 one), and the two branches' post-2026-07-21 entries kept as two contiguous newest-first blocks (`mamma-photo-viewer`'s continuation first, then `master`'s) rather than interleaved by raw timestamp — same convention the file's own header already prescribes ("never rewrite or reorder past entries in either half").
- Per Joakim's standing instruction (2026-07-23): when a bug like this is found, always trace it to its actual root cause (which commit, why) before fixing it — not just patch the symptom. Applied here via `git show <rev>:path`/`git log -S` bisection across both branches' history rather than assuming "the merge did it."
- **No structural check added yet** — this bug's root cause (a silent top-insert past a structural paragraph) is still fully reproducible by the next `CHANGELOG.md` edit, by hand or by a future AI session, since nothing enforces "header paragraph stays at the top" or "entries stay in descending timestamp order." Worth a lightweight check (e.g. in `tools/documentation_checks`) if this recurs.
