# Skipped app-tests rerun before the second commit this session

See [README.md](../README.md) for what belongs here.

## What happened

This session made two commits touching `prototypes/upload-and-share-mockup/` (`aaaf707`, then `8b7ae9f`). `app/tests` was run once, before the first commit (58 passed), but not re-run before the second. `documentation/tooling/README.md`'s wrap-up table gives `app/tests` no skip exception ("before every commit, docs-only or not") — unlike the adjacent `server/tests` row, which explicitly allows skipping a rerun against unchanged code within the same session. Caught during session wrap-up, not in the moment; re-run at wrap-up time and still 58 passed (`app/` code never actually changed this session), so no regression slipped through, but the *check* itself was skipped when it should have run.

## Why it happened

Read `server/tests`' skip-if-already-clean exception and applied the same reasoning to `app/tests` by analogy, without checking that the table gives the two rows different rules. The CLAUDE.md prose (single paragraph covering both suites) reads ambiguously on this point too — the "skip re-running" clause is placed right after the `server/tests` sentence, so it's not obvious at a glance whether it's meant to cover just that suite or both.

## What changed

`documentation/tooling/README.md`'s `app/tests` row and CLAUDE.md's TDD bullet already state the no-skip rule correctly on close reading; the gap was in applying it, not in what's written. No doc change made here — logged so a future session's wrap-up sweep catches the same substitution error if it recurs, and so "the two test-suite rows have different skip rules, read each independently" is on record rather than re-discovered.
