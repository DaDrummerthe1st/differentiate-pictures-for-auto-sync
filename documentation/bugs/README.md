# bugs/

A landing spot for bugs found in the moment — during a live session,
mid-deploy, wherever — that haven't been triaged into their proper home
yet (a topic folder's own `TODO.md`, `DEFERRED.md`, or a real fix). This
folder is deliberately not organized by topic; it's a capture point, not
a filing system. See [TODO.md](TODO.md) for the current untriaged list.

For a bug complex enough to need a multi-session investigation trail
(not just a one-line description), give it its own file under
[reports/](reports/) — named `<date>-<short-slug>.md` — and link it from
the `TODO.md` entry instead of inlining the whole history there. The
report is where the *process* (what was checked, what was ruled out, in
order) lives, not just the conclusion — see
[reports/2026-07-17-thumbnail-oom-under-load.md](reports/2026-07-17-thumbnail-oom-under-load.md)
for the shape to follow.

Use `tools/new_bug_report/new_bug_report.sh "Short bug title"` to create
one with a consistent name and the right starter template — don't
hand-name these.

Once a bug here gets prioritized, it moves to wherever it actually
belongs (e.g. `documentation/photo-server/TODO.md` or `DEFERRED.md`) and
gets removed from this file — this folder should tend toward empty, not
grow forever.
