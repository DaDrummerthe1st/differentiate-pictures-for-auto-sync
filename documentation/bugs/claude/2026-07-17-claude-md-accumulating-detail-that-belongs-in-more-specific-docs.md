# CLAUDE.md accumulating detail that belongs in more specific docs

Status: **all 3 flagged candidates resolved 2026-07-19** (2 trimmed, 1 found already absent). The "not evaluated" push-policy bullet below is still genuinely unevaluated.

## What Joakim flagged

"Instructions shall live where they should live, not in the CLAUDE.md!" — raised 2026-07-17 after this session added several detailed bullets directly into `CLAUDE.md` rather than keeping it lean with a pointer to where the real explanation lives. This conflicts with this project's own stated principle ("Lean, exact, and compact... no duplication between files") that CLAUDE.md itself already asserts elsewhere.

## Specific candidates added today, worth reviewing/trimming next session

- The `documentation/bugs/TODO.md` periodic-check bullet — the reasoning for *why* `bugs/` exists belongs in `bugs/README.md` (which already has it); CLAUDE.md probably only needs "check `bugs/TODO.md` every session, see its own README for how." **Resolved, but not by trimming** — checked 2026-07-19 (`grep -n "bugs/TODO" CLAUDE.md` returns nothing): no such bullet exists in CLAUDE.md as it stands today, so either it was removed in an earlier, undocumented pass, or never actually landed there. Nothing left to trim.
- The "every bug/lapse is its own file" bullet — this is **already fully duplicated** in both `bugs/README.md` and `bugs/claude/README.md`. CLAUDE.md restating the whole rule is exactly the duplication this project says not to do; a one-line pointer would suffice. **Fixed 2026-07-19** — trimmed to a one-line pointer at both targets.
- The wrap-up coverage-check bullet — the mechanics of what `check_coverage.sh` does belongs in `tools/commit_cost`'s own documentation (`documentation/tooling/COMMIT_COST.md`), not spelled out again in CLAUDE.md. **Fixed 2026-07-19** — folded into a single pointer bullet at [documentation/tooling/README.md](../../tooling/README.md), which now also holds the full wrap-up checklist (a broader consolidation than originally scoped here, prompted by a separate conversation about wrap-up cadence the same day).

## Not evaluated

Whether the push-policy bullet (2026-07-17, "let claude do the pushes") belongs fully in CLAUDE.md as-is — that one arguably *is* core working-agreement material, not detail that belongs elsewhere. Worth confirming that distinction (working-agreement rule vs. explanatory detail) rather than trimming everything uniformly.

## Next session should start with

Reread CLAUDE.md in full, identify every bullet that restates content already fully written elsewhere, and replace with a short pointer - keeping only the actual working-agreement decision (what to do) in CLAUDE.md, not the reasoning/mechanics (why, how), which belongs in the specific doc that already has it.

## What changed

Two of the three candidates were trimmed to one-line pointers (the "every bug/lapse is its own file" bullet, and the wrap-up coverage-check bullet, folded into `documentation/tooling/README.md`'s new wrap-up checklist); the third was found already absent. The push-policy bullet was deliberately left as-is pending the "not evaluated" question above.
