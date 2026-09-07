# Design swipe-to-triage gesture and recoverability model for the Kotlin app

New `mobile/UX_FLOWS.md` (Joakim's explicit request: UX design rules get their own documentation
dimension, not folded into architecture/backlog notes) designing the swipe-to-declutter gesture:
a two-way swipe (remove-from-view vs. organize/tag) and a two-tier recoverability model (immediate
undo + a durable, manual-only-purge "Removed" bin) satisfying his hard always-recoverable rule.
Researched Apple Photos' and Google Photos' own recently-deleted retention conventions (30/60 days)
as precedent, then proposed going stricter (no auto-purge by default) given the rule was stated as
non-negotiable. Two open questions flagged for Joakim: left/right direction mapping, and whether an
optional auto-purge timer should exist. `TODO.md`'s inline sketch replaced with a pointer to avoid
duplication.

- **Doc size**: `mobile/UX_FLOWS.md` new file, 6314 chars. `mobile/TODO.md` -283 chars.
  `mobile/README.md` +98 chars.
