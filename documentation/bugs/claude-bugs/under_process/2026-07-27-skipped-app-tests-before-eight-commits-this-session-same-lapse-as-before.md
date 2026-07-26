# Skipped app/tests before eight commits this session, same lapse as before

See [README.md](../README.md) for what belongs here.

## What happened

CLAUDE.md: "Run the fast in-process `app/tests` before every commit, even a
docs-only one." This session (branch `tags`, 2026-07-27) made 8 commits — a
claude-bugs report, a CLAUDE.md rule update, the new `documentation/tags/` folder,
a `DATA_DICTIONARY.md` consolidation, a cross-reference pass, a redundancy fix, and
the `doc_metrics`/`commit_cost` ledger commits interleaved between them — before
running `app/tests` even once. Only caught during the session-wrap-up checklist
pass, after all 8 commits already existed.

This is the same lapse as
[2026-07-26-skipped-the-mandatory-app-tests-run-before-four-earlier-commits-this-session.md](../fixed/2026-07-26-skipped-the-mandatory-app-tests-run-before-four-earlier-commits-this-session.md),
one session earlier, whose own "What changed" section was: run the suite, "check it
actually ran this session before assuming it did." That's exactly what didn't
happen this time either — the same docs-only reasoning recurred, unchecked against
either the rule's literal text or that prior bug file, until wrap-up.

## Why it happened

The previous fix was behavioral only ("be more careful, check next time") with no
structural enforcement — nothing actually stops a docs-only session from reaching
its 8th commit without the check ever firing, so the same "nothing here could touch
`app/tests`" reasoning that caused the first occurrence had nothing new to trip over
the second time. A purely in-session correction doesn't survive into a fresh session
with no memory of it; only something checked in (a rule, a hook, a checklist gate
that's actually consulted mid-session rather than only at wrap-up) would.

## What changed

Ran `.venv-test/bin/python -m pytest app/tests/ -q` (58 passed, no regressions —
same "safe in hindsight, not because the process worked" caveat as last time).
**Not yet fixed structurally** — flagged to Joakim in-session rather than
unilaterally adding a pre-commit hook or similar enforcement mechanism, since that's
a tooling/process change beyond this session's actual task (tag taxonomy design) and
worth his input on the mechanism (a git hook, a stronger CLAUDE.md placement, a
TodoWrite item auto-seeded at session start) rather than picked unilaterally. Left
`under_process`, not `fixed`, until a structural fix actually lands — the previous
occurrence closing itself out as "fixed" on a behavioral-only change is arguably why
it recurred at all.
