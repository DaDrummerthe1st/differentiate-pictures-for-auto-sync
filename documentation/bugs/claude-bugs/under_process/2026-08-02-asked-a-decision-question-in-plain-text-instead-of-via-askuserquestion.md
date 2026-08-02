# Asked a decision question in plain text instead of via AskUserQuestion

See [README.md](../README.md) for what belongs here.

## What happened

While discussing where a new `resources/test_pictures` fixture directory should live (in-repo-gitignored vs. fully outside the repo), Joakim's constraint was that it must never be committed *and* never be noted anywhere in the repo's own documentation. In the same reply, I raised a genuine binary decision only Joakim could make — whether I should note the directory's existence in my private, non-repo memory store instead — but asked it as a plain-text question at the end of my response ("Want me to do that, or would you rather it stay completely unmentioned anywhere, repo or not?") instead of via the `AskUserQuestion` tool. Joakim flagged this directly: "this should've been a AskUserQuestion. Bug report it. No, I do not want you to change it" — and declined the option (leave it unmentioned everywhere, repo or memory).

## Why it happened

The global working-preferences file (`~/.claude/CLAUDE.md`) points to `claude-md/ask_ui.md` for the "Questions/popup UI" rule, but that file does not exist at that path (confirmed while writing this report) — so the rule's actual content wasn't loaded or checked before asking. Separately, in the moment, the question felt like a natural trailing sentence appended to an explanation rather than a standalone decision point, so it didn't register as the kind of "genuinely the user's to make" fork the popup UI is for.

## What changed

- Flagged the broken cross-reference to Joakim: `~/.claude/CLAUDE.md` links to `claude-md/ask_ui.md`, which doesn't exist — that file needs to be created or the pointer fixed so the actual rule content is checkable, not just assumed. (Out of this repo's scope to fix directly; global config.)
- Going forward in this repo: any reply that raises a fork only Joakim can resolve — including one appended almost incidentally to an explanation, not just ones framed up front as a question — routes through `AskUserQuestion`, not inline prose.
