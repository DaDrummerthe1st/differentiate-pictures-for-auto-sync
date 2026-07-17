# CLAUDE.md accumulating detail that belongs in more specific docs

Status: **priority check for next session, not fixed today**.

## What Joakim flagged

"Instructions shall live where they should live, not in the CLAUDE.md!"
— raised 2026-07-17 after this session added several detailed bullets
directly into `CLAUDE.md` rather than keeping it lean with a pointer to
where the real explanation lives. This conflicts with this project's own
stated principle ("Lean, exact, and compact... no duplication between
files") that CLAUDE.md itself already asserts elsewhere.

## Specific candidates added today, worth reviewing/trimming next session

- The `documentation/bugs/TODO.md` periodic-check bullet — the
  reasoning for *why* `bugs/` exists belongs in `bugs/README.md` (which
  already has it); CLAUDE.md probably only needs "check `bugs/TODO.md`
  every session, see its own README for how."
- The "every bug/lapse is its own file" bullet — this is **already
  fully duplicated** in both `bugs/README.md` and `bugs/claude/
  README.md`. CLAUDE.md restating the whole rule is exactly the
  duplication this project says not to do; a one-line pointer would
  suffice.
- The wrap-up coverage-check bullet — the mechanics of what
  `check_coverage.sh` does belongs in `tools/commit_cost`'s own
  documentation (`documentation/tooling/COMMIT_COST.md`), not spelled
  out again in CLAUDE.md.

## Not evaluated

Whether the push-policy bullet (2026-07-17, "let claude do the pushes")
belongs fully in CLAUDE.md as-is — that one arguably *is* core working-
agreement material, not detail that belongs elsewhere. Worth confirming
that distinction (working-agreement rule vs. explanatory detail) rather
than trimming everything uniformly.

## Next session should start with

Reread CLAUDE.md in full, identify every bullet that restates content
already fully written elsewhere, and replace with a short pointer -
keeping only the actual working-agreement decision (what to do) in
CLAUDE.md, not the reasoning/mechanics (why, how), which belongs in the
specific doc that already has it.
