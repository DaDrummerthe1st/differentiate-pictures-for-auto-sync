# Shared sqlite3 connection unsynchronized across concurrent request threads

Status: **fixed same session, 2026-08-08**.

## Symptom

`app/tests/test_thumb_concurrency.py::test_concurrent_thumbnail_generation_is_limited` (two
simultaneous `GET /thumb` requests, fired from two threads) started flaking after adding the admin
photo-source setting. Real failure captured:

```
File "app/main.py", line 212, in get_active_photos_root
    candidate = (PHOTOS_LIBRARY_ROOT / _get_active_source()).resolve()
TypeError: unsupported operand type(s) for /: 'PosixPath' and 'NoneType'
```

`_get_active_source()` read `active_source` back as `None` from a column declared `NOT NULL DEFAULT
'dpfas_media'`, with a row already seeded at module import — not a logical "row missing" case (that
branch already handles it via `if row else DEFAULT_ACTIVE_SOURCE`), a genuinely corrupted read.

## Investigation log

1. `app/main.py`'s `db = sqlite3.connect(DB_PATH, check_same_thread=False)` is one module-level
   connection, shared by every request. FastAPI runs sync endpoints in a real OS threadpool, so two
   concurrent requests genuinely call into this same `sqlite3.Connection` object from two different
   threads at once.
2. This was already true before this session — `log_requests` (the request-logging middleware) has
   always run `db.execute(...)`/`db.commit()` on *every* request, unsynchronized, including both
   threads' requests in the flaky test above. That test passed reliably before this session anyway;
   the middleware's own concurrent access was apparently rare/cheap enough in practice not to
   visibly corrupt anything.
3. This session added a second concurrent DB touch to the exact same request path:
   `resolve_relpath` (called by `/thumb`) now calls `get_active_photos_root()` →
   `_get_active_source()`, a `db.execute(...).fetchone()` read - hit alongside the middleware's write, on
   the same two threads, in the same test. That's what tipped a previously-rare race into a reliably
   reproducible one (15/15 clean runs after the fix below; was failing intermittently before it).
4. Confirmed real, not a test-ordering artifact: reran the single failing test 15 times in isolation
   after the fix (`for i in $(seq 1 15); do pytest app/tests/test_thumb_concurrency.py -q; done`) -
   clean every time.

## Fix

Added `_db_lock = threading.Lock()` and wrapped every request-time `db.execute`/`db.commit` call
site in `app/main.py` (12 functions: `_log_event`, `log_requests` middleware, `_get_active_source`,
`set_photos_source`, `list_tags`, `tag_value_suggestions`, `create_tag`, `update_tag`, `delete_tag`,
`upload_photo`'s sibling `upload_voiceover`, `list_voiceovers`, `get_voiceover`) with `with
_db_lock:`. Module-load-time schema setup (`CREATE TABLE IF NOT EXISTS ...`, the `app_settings` seed
row) is exempt — it runs once, single-threaded, before the server accepts any requests, so there's
nothing to race there.

Deliberately a single global lock around the whole shared connection, not per-table or
per-statement-type locking — this app is two real users at low request volume (see
`documentation/photo-server/README.md`), so fully serializing DB access has no measurable cost, and a
single lock is much easier to reason about as actually correct than trying to prove finer-grained
locking is safe.

## Verification

`.venv-test/bin/python -m pytest app/tests/ detector/tests/ -q` — 133 passed, and
`test_thumb_concurrency.py` specifically re-run 15x clean (see investigation log #4).

## Next session should start with

Nothing outstanding — fixed and verified same session. If a *new* concurrent-DB-touching endpoint is
ever added to `app/main.py`, it needs `with _db_lock:` around its `db.execute`/`db.commit` calls too;
there's no automatic enforcement of this (e.g. a lint rule) — this file is the only record of the
convention existing at all.
