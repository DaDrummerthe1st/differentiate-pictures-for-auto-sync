# bugs/

A landing spot for bugs found in the moment — during a live session,
mid-deploy, wherever — that haven't been triaged into their proper home
yet (a topic folder's own `TODO.md`, `DEFERRED.md`, or a real fix). This
folder is deliberately not organized by topic; it's a capture point, not
a filing system.

**Hard rule (2026-07-17): every bug is its own file under
[reports/](reports/), named `<date>-<short-slug>.md` — never a bullet
added to a shared list.** This applies even to a one-line bug, not just
multi-session investigations — the file is where the *process* (what
was checked, what was ruled out, in order) lives as it's learned, not
just the conclusion — see
[reports/2026-07-17-thumbnail-oom-under-load.md](reports/2026-07-17-thumbnail-oom-under-load.md)
for the shape to follow. No separate index is kept — see
[TODO.md](TODO.md) for why (it proved unreliable) and how to browse
what's open instead.

Use `tools/create_bug_report/create_bug_report.sh "Short bug title"` to create
one with a consistent name and the right starter template — don't
hand-name these. Once a `reports/` file is genuinely resolved (not just
mitigated), move it with `tools/create_bug_report/mark_solved.sh
<filename>` into [solved/](solved/README.md) instead of deleting it —
see that folder's README for why.

[claude/](claude/README.md) is a different, narrower thing: not app
bugs, but the AI session's own process lapses — a routine that should
have run per an existing rule and didn't, or a claim made without
properly checking it first. See that folder's own README for the
distinction and what each entry should end with.

Once a bug here gets prioritized, it moves to wherever it actually
belongs (e.g. `documentation/photo-server/TODO.md` or `DEFERRED.md`) and
gets removed from this file — this folder should tend toward empty, not
grow forever.
