# Wrote multi-sentence changelog entries instead of one or two lines

See [README.md](../README.md) for what belongs here.

## What happened

During a full documentation-cleaning pass, wrote 7 changelog entries (`tools/create_changelog_entry/create_changelog_entry.sh`) for the session's commits. `documentation/changelog/README.md`'s own stated convention is "What + why, one or two lines — same discipline the old `CHANGELOG.md` used." Every entry instead ran 2-4 full sentences of prose (paraphrasing the commit's own reasoning) plus a doc-size stats line, totaling 5,585 characters across the 7 files (613-1,340 chars each). Joakim caught it: "why would you need to write a changelog of 5,5xx chars?! Write the usual lines, invent better ways to point to files."

## Why it happened

Treated the changelog entry as a second place to fully re-explain the change (duplicating the commit message's own "why" paragraph) rather than as a short pointer alongside a commit that already carries the full explanation. The doc-size stat line is a genuine CLAUDE.md/WORKFLOW.md requirement ("report the character-count change... in the changelog entry"), but the surrounding "what + why" prose grew well past the one-or-two-line bar the convention actually asks for, and nothing prompted a check against that specific line before writing each entry.

## What changed

Not fixing the 7 existing entries — changelog entries are append-only, and Joakim explicitly said not to touch them (only to file this report). Going forward: a changelog entry's "what + why" stays to one or two lines, full stop — the commit message (already written in full, already permanent, already `git log`-able) is where the complete reasoning belongs, not a second retelling in the changelog file. The entry should point at specifics rather than restate them: name the file(s) touched and, where it aids a fast skim, the exact character delta — not a paragraph of narrative. `documentation/changelog/README.md`'s convention line already said this; the fix here is discipline in applying it, not new wording.
