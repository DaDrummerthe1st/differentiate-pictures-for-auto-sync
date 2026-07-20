# Missed CHANGELOG entries for a stretch of commits

## What happened

A run of ~8 commits (the localStorage revert, the full `bugs/claude/` setup, the `bugs/` one-file-per-bug restructuring, the coverage-check script, several `CLAUDE.md` updates) went out with no `CHANGELOG.md` entry for any of them, despite CLAUDE.md's non-negotiable "one revision per update" rule. Joakim caught the gap by asking directly.

## Why it happened

Same shape as the missed commit_cost logging earlier in this session: a fast-moving stretch of small, related commits, and the "update CHANGELOG.md" step quietly fell out of the loop with nothing forcing it back in.

## What changed

A consolidated CHANGELOG entry was added covering the missed stretch. No systematic prevention built yet, unlike the commit_cost gap (which got `check_coverage.sh`) — CHANGELOG entries aren't 1:1 with commits (some commits legitimately don't need one), so a mechanical coverage check doesn't apply the same way. Still an open gap: this class of lapse (a required per-commit-ish step silently dropping out during a fast multi-commit stretch) has now happened twice in one session, for two different routines - worth a session-wrap-up habit of explicitly re-reading CLAUDE.md's non-negotiables list before considering wrap-up done, not just running the scripts that exist.
