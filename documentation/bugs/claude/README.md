# bugs/claude/

Not application bugs — **process lapses by the AI session itself**:
times a routine that should have happened (per CLAUDE.md, POLICY.md, or
plain diligence) didn't, or something was claimed without being properly
checked first. The point isn't blame, it's improving the actual
documentation/rules so the same lapse doesn't recur.

**Hard rule (2026-07-17): every lapse is its own file in this folder,
named `<date>-<short-slug>.md` — never a bullet added to a shared list.**
[LOG.md](LOG.md) is only an index (one line + link per entry); it should
never grow a real write-up inline. Use
`tools/new_bug_report/new_bug_report.sh --claude "Short title"` to
create one with the right template — don't hand-name these. Every entry
should end with what changed (a CLAUDE.md rule tightened, a routine made
more explicit, a check added) as a result.

If a lapse turns out to be a real tool/code bug rather than the AI
session's own process failure (e.g. a script silently failing), it
belongs in [../TODO.md](../TODO.md) instead — this folder is
specifically for "the session should have done X per an existing rule,
and didn't."
