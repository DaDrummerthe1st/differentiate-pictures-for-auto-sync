# Plan-mode review comments not rendered as Markdown, action buttons unreachable

See [README.md](../README.md) for what belongs here.

Environment: VS Codium extension (VS Code native extension environment), Claude
Code's plan-mode `ExitPlanMode` review UI.

## What happened

During a plan-mode review (this session's tag-taxonomy design plan), Joakim left
long free-text comments responding to specific quoted lines of the proposed plan.
Two problems, reported by him mid-session:

1. Those long answers were displayed as raw, un-rendered text rather than through
   Markdown, unlike normal chat/plan text elsewhere in the UI.
2. After submitting that feedback, the review UI showing the list of proposed
   changes had no reachable accept/reject (or equivalent) action controls — the
   change list was visible but nothing on it could be acted on.

Both are UI/rendering behavior of the Claude Code VS Codium extension itself, not
this project's code or docs.

## Why it happened

Not diagnosed from this session — no access to the extension's own source/rendering
pipeline from here. Flagged as observed behavior for whoever triages it upstream.

## What changed

Not a fixable-from-this-repo issue. Filed here so the observation isn't lost, and
queued for Joakim to report upstream at
https://github.com/anthropics/claude-code/issues per this project's standing
practice of routing Claude Code tool feedback there (see global CLAUDE.md's
"give feedback" pointer) rather than the AI session filing it directly.
