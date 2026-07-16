# Changelog — mamma-photo-viewer branch

One entry per revision, newest first. Started 2026-07-17 — branch history
before this point lives only in `git log` (this branch skipped the
CHANGELOG discipline the main branch already has, for speed early on; see
CLAUDE.md's project-memory note on that trade-off).

## 2026-07-17

- Removed the zip-download feature entirely — server endpoint, client JS,
  tests, and its docker volume — in favor of the sequential per-file
  transfer already used elsewhere. Confirmed by Joakim as a permanent
  decision (mum's real download over a slow/USB-drive link showed a
  single zip is all-or-nothing on failure), not a workaround. Split the
  voiceover feature's docs out of `documentation/gui/TODO.md` into their
  own `documentation/gui/voiceover/` subfolder. Fixed a stale test count
  left in `documentation/gui/README.md` (29 -> 24) from the zip-test
  removal. Commit `1945976`.
- Docker cleanup: the zip removal above left two dead zipcache volumes
  behind — this project's own (10.24GB, only detached once the container
  was recreated on the updated compose file) and a second copy on
  `mamma-photo-viewer_zipcache` (5.08GB), orphaned since the
  branch-mixup incident (see TODO.md's history note) left behind the old
  sibling-repo container's volumes with no container attached. Removed
  both, plus that same orphaned container's `_thumbcache`/
  `_analytics_data` volumes and its unused image, 2 empty unattached
  anonymous volumes, and stopped this repo's own `photo_server_test_pg`/
  `_redis` fixtures (forgotten running 19h past their test session, via
  their own `scripts/test_db.sh down` / `test_redis.sh down`). Local
  Docker volume usage: 15.56GB -> 129.8MB. `buzzkit-api`'s `api-worker-1`
  (a different project) was found still crash-looping under
  `unless-stopped` on missing config — left untouched, flagged to
  Joakim, not this repo's concern to fix.
- Project-level Claude Code permission settings (`.claude/settings.json`,
  tracked in git): added a blanket `Bash(*)` allow and
  `/var/lib/docker/volumes` to `additionalDirectories`, after a session
  where routine investigative commands kept hitting permission popups.
  Note for next session: destructive commands (`docker volume rm`,
  `docker rmi`, `docker run`) stay gated regardless — that floor isn't
  configurable from settings, by design.
