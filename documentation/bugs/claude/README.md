# bugs/claude/

Not application bugs — **process lapses by the AI session itself**: times a routine that should have happened (per CLAUDE.md, POLICY.md, or plain diligence) didn't, or something was claimed without being properly checked first. The point isn't blame, it's improving the actual documentation/rules so the same lapse doesn't recur.

**Hard rule (2026-07-17): every lapse is its own file in this folder, named `<date>-<short-slug>.md` — never a bullet added to a shared list.** Use `tools/create_bug_report/create_bug_report.sh --claude "Short title"` to create one with the right template — don't hand-name these. Every entry should end with what changed (a CLAUDE.md rule tightened, a routine made more explicit, a check added) as a result. No index is kept (tried one, `LOG.md` — removed 2026-07-17 after it drifted out of sync twice in a row within the same session; `ls` this directory directly instead, the filenames are self-describing).

If a lapse turns out to be a real tool/code bug rather than the AI session's own process failure (e.g. a script silently failing), it belongs in [../TODO.md](../TODO.md) instead — this folder is specifically for "the session should have done X per an existing rule, and didn't."
