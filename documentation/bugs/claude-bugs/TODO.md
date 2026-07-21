# bugs/claude-bugs/TODO.md

No index is kept here — it proved unreliable (drifted out of sync repeatedly; `LOG.md` was removed 2026-07-17). Browse [under_process/](under_process/) directly for what's still open — filenames are `<date>-<short-slug>.md`, self-describing.

**Candidate, not done**: adopt a `Status:` line at the top of every entry, same as `../repo/`'s files already have, instead of relying on a "What changed" section's presence/wording. Raised 2026-07-21 after splitting `claude/` into `fixed/`/`under_process/` required reading each file's tail in full to judge whether it was actually resolved — a mechanical `Status:` line would have made that a grep instead of 13 full reads.
