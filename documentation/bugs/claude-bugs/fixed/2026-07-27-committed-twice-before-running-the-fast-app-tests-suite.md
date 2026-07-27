# Committed twice before running the fast app/tests suite

See [README.md](../README.md) for what belongs here.

## What happened

Built `prototypes/mockup/` (a photo-tagging showcase, doesn't touch `app/`) and,
per this project's own commit-continuously rule, made two commits in a row —
the mockup itself, then a follow-up logging `doc_metrics`/`commit_cost` — without
running `python3 -m pytest app/tests` before either one. CLAUDE.md is explicit:
"Run the fast in-process `app/tests` before every commit, even a docs-only one."
Only noticed the gap afterward, while reviewing the session for the wrap-up
sweep, and ran the suite retroactively (58 passed — no actual regression, but
that's luck, not process).

## Why it happened

The change had already been verified thoroughly by other means — a Selenium
harness drove every interactive flow in the new mockup and checked for browser
console errors, which felt like "the testing for this change" was done. That
reasoning silently substituted for the unrelated, unconditional `app/tests` gate,
which the rule doesn't make conditional on "does this change plausibly affect
`app/`" — it says every commit, docs-only or not. This is the same shape of
lapse as the 2026-07-19 incident (`documentation/bugs/claude-bugs/fixed/2026-07-19-skipped-tdd-for-a-small-helper-reasoning-it-wouldn-t-matter.md`),
which had already removed a "where practical" qualifier from the TDD rule to
close exactly this kind of self-granted exception — the wording was already
unambiguous; a second, differently-rationalized exception found its way through
anyway. Wording-only fixes don't close this class of lapse reliably; nothing
mechanical was checking it.

## What changed

Added `.githooks/pre-commit` — runs `app/tests` and blocks the commit on
failure, so the rule no longer depends on the AI session (or a human) both
remembering *and* not talking themselves out of it in the moment. It only
reminds (doesn't block) about `server/tests` for `server`/`app`-touching
commits, since that suite is container-based/slower and the rule's "skip if
already run clean this session" call isn't mechanically checkable. Documented
in `documentation/tooling/README.md`, including the one-time
`git config core.hooksPath .githooks` setup Joakim needs to run himself (an AI
session can't change git config per CLAUDE.md's git safety protocol — so this
still isn't self-activating without that step).
