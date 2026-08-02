# Fix stale Redis/test-count/Dockerfile-path claims, compact resolved branch-merge history in photo-server docs

Full-repo cleaning pass, architecture-docs scope. `photo-server/README.md` still listed the Redis persistent-volume bug as open though it was fixed 2026-07-21; `gui/README.md`'s test count (53) was stale (actual 58); `DEFERRED.md` cited a nonexistent `app/Dockerfile`. Also compacted `TODO.md`'s fully-resolved branch-merge history section and a duplicate Redis-revocation note in `DEFERRED.md` that already had a canonical copy in `TODO.md` 1.9b.

- **Doc size**: photo-server/README.md 5,822 → 5,725; photo-server/DEFERRED.md 11,420 → 11,253; photo-server/TODO.md 43,746 → 41,280; gui/README.md 9,233 → 9,233 (test-count fix, same length). Combined: −2,730 chars.
