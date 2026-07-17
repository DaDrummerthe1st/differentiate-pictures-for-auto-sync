# bugs/TODO.md — untriaged index

Every bug is its own file under [reports/](reports/) — this file is
just an index (one line + link each), never the write-up itself. See
[README.md](README.md) for how this works, and
`tools/new_bug_report/new_bug_report.sh` to create a new one.

Entries below are listed in the order found, not priority — **start
here instead** if picking this up fresh:

1. **Highest-value next step**: [pre-compile thumbnails ahead of
   time](reports/2026-07-17-pre-compile-thumbnails-ahead-of-time.md) —
   the biggest remaining real gap between where this is now and
   Elisabeth having a smooth experience. Three design decisions are
   already identified there; start by making those calls, then TDD it.
2. **Quick, safe, worth doing early**: the two deploy-path bugs
   ([Postgres schema
   init](reports/2026-07-17-postgres-schema-never-initialized-in-production.md),
   [`server/Dockerfile` missing
   `scripts/`](reports/2026-07-17-dockerfile-missing-scripts-directory.md))
   — both have a working documented workaround already (`DEPLOYMENT.md`
   steps 4-5), so this is "wire the known fix into the Dockerfile/CMD
   properly," not fresh investigation.
3. Everything else below is real but lower urgency — the app works for
   tonight without any of them.

## Index

- [`tools/commit_cost` stops finding commit boundaries partway through a long session](reports/2026-07-17-commit-cost-boundary-detection-breaks-on-long-sessions.md)
- [Postgres schema was never initialized in production](reports/2026-07-17-postgres-schema-never-initialized-in-production.md)
- [`server/Dockerfile` never copies `scripts/` into the image](reports/2026-07-17-dockerfile-missing-scripts-directory.md)
- [Thumbnails fail under concurrent load, likely OOM](reports/2026-07-17-thumbnail-oom-under-load.md) — mitigated + a real fix applied, same day
- [Faster/leaner thumbnail generation](reports/2026-07-17-faster-leaner-thumbnail-generation.md)
- [Pre-compile thumbnails ahead of time, not on-demand](reports/2026-07-17-pre-compile-thumbnails-ahead-of-time.md)
- [No log persistence guarantee across the stack](reports/2026-07-17-no-log-persistence-across-stack.md)
- [No resource monitoring / alerting for the deployed stack](reports/2026-07-17-no-resource-monitoring-alerting.md)
- [Support/help button, not built](reports/2026-07-17-support-help-button-not-built.md)
- [Unauthenticated static UI shell loads before any login check](reports/2026-07-17-unauthenticated-static-shell-before-login.md)
