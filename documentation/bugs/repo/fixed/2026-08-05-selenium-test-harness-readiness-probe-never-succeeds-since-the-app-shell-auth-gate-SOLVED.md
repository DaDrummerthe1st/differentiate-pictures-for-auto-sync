# Selenium test harness readiness probe never succeeds since the app-shell auth gate

Status: **fixed, 2026-08-05, same session it was found in.**

## Symptom

Running any Selenium test (including pre-existing, unmodified ones like `test_album_switching.py`)
timed out after 15s with `RuntimeError: app server did not come up on http://127.0.0.1:<port>`, even
though the server logs showed uvicorn was actually up and answering requests fine.

## Investigation log

1. Found while adding this session's new tag-UI Selenium tests
   (`app/tests_selenium/test_tag_ui.py`) - ran an *unmodified* existing test file first
   (`test_album_switching.py`) to rule out something wrong with the new tests specifically, and it
   failed identically, proving this was a pre-existing harness regression, not anything about the new
   tests.
2. `app/tests_selenium/conftest.py`'s `app_server` fixture polls `urllib.request.urlopen(base_url + "/")`
   in a loop until it returns without raising, treating any exception as "not up yet, keep retrying."
3. `git log` on `documentation/bugs/repo/fixed/2026-07-17-unauthenticated-static-shell-before-login.md`
   found commit `992ef140` (2026-07-23), "Gate the app shell behind a server-side session check" -
   `GET /` now redirects (307) an unauthenticated request to `/login` instead of always serving
   `index.html`. That commit updated `app/tests/test_auth_gate.py` (the in-process `TestClient` suite)
   but never touched `app/tests_selenium/conftest.py`'s readiness probe.
4. `/login` isn't a route this app (`app/`, the filesystem-based photo-viewer) serves at all - that
   page belongs to the separate `server/` auth backend, a different codebase/container entirely. So an
   unauthenticated `GET /` now always resolves to `GET /login` -> `404`.
5. `urllib.error.HTTPError` is a subclass of `urllib.error.URLError`. The probe's `except
   (urllib.error.URLError, ConnectionError)` clause therefore also swallowed the 404 from that redirect
   chain and treated it as "server not up yet, retry" - so the loop span the full 15s and then failed,
   on every single run, regardless of whether uvicorn was actually healthy.

## Root cause

The readiness probe's success condition (`GET /` returns 200) stopped being reachable the moment `GET /`
started requiring a session (2026-07-23), but the probe itself was never updated to match - a
regression introduced by that commit that had gone unnoticed because (per the "Branch relationship"
history in `documentation/photo-server/TODO.md`) the branches doing GUI/Selenium work and the branch
that added the auth gate diverged and were only reconciled well after the fact, and nothing re-ran the
Selenium suite for real after that reconciliation to notice it had gone dark.

## Fix

`app/tests_selenium/conftest.py`: catch `urllib.error.HTTPError` *before* the broader
`(URLError, ConnectionError)` clause and treat it as "server is up" - receiving any real HTTP response
(even a non-2xx one) proves uvicorn is listening and answering, which is all this probe ever needed to
confirm before letting a test start driving a real browser against it. Confirmed fixed: re-ran
`test_album_switching.py` (unmodified) and it passed, then the full `app/tests_selenium/` suite (18
tests, including this session's 5 new tag-UI ones) all passed.

## Why this went unnoticed until now

Nothing in the ordinary TDD workflow (`.venv-test/bin/python -m pytest app/tests/ -q`, run constantly)
touches `app/tests_selenium/` at all - that suite only runs when someone explicitly brings up
`scripts/test_selenium.sh` first, which apparently hadn't happened in the roughly two weeks between the
992ef140 auth-gate commit and this session, across several sessions that documented Selenium test files
as "built"/"covered" without this being caught. Worth flagging for whoever next touches the Selenium
suite: run it for real at least once per session that touches `app/static/` or `app/main.py`'s auth
gating, not just assume it still works because the code compiles.
