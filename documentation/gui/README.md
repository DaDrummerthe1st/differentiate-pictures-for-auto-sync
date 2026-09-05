# documentation/gui/

**Superseded 2026-09-05 by the native-app pivot** — see [../VISION.md](../VISION.md)'s
2026-09-05 note. `app/` (and everything else this file describes) is archived,
code-disregarded reference at
[../../previous-work/multi-user-web-app/](../../previous-work/multi-user-web-app/README.md).
Read as history of what was built, not as the current or planned GUI.

The photo-server GUI's first working version — code name `mamma-photo-viewer`, built 2026-07-16. Despite prior GUI planning existing elsewhere in this repo (`documentation/photo-server/MOCKUP.md` and its TODO's GUI-coverage items), this is the first version that actually runs, so **this is the leading source for how the GUI is supposed to work** — treat those earlier planning docs as superseded where they conflict with what's built and documented here.

Code lives at the repo root on `master` (`app/`, `Dockerfile`, `docker-compose.yml`, `requirements.txt`) rather than under a subdirectory, since it started as a separate repo before ending up here (see TODO.md's history note). The `mamma-photo-viewer` branch this work originally happened on was fully reconciled into `master` and deleted 2026-08-05 (see TODO.md's "Branch state" note) — `master` is now the only branch. Root `README.md` carries the normal project pitch plus a section pointing back here for this work.

## What it is

Single-container, no-login web app for browsing a photo library and picking files to keep. Built for Joakim's mum to browse `mammas_bilder` (thousands of family photos) and download the ones she wants — but the underlying mechanics (album grouping, media-type handling, bulk download, in-picture voice narration) are meant to generalize to the real photo-server GUI, not stay one-off.

**Stack**: FastAPI + vanilla JS, with jQuery and Bootstrap vendored in as of 2026-07-21 (self-hosted under `app/static/vendor/`, no CDN — see `TODO.md`; still no frontend framework, no build step), session-gated behind a separate auth backend (`server/`, JWT cookie, shared secret — see `app/auth.py`). The photo-viewer's own `Dockerfile` still bakes in a self-signed cert as a fallback, but neither the local (`docker-compose.yml`, Caddy on plain `http://localhost`) nor production (`docker-compose.prod.yml`, Caddy with a real Let's Encrypt cert) deployment actually uses it — both terminate TLS (or skip it, on localhost) at Caddy instead. A secure browser context is still required either way, for the folder-picker and microphone features.

**Run it — full local stack, fixed 2026-07-23**: the repo-root `docker-compose.yml` now runs the whole thing locally (caddy + photo-viewer + this branch's auth backend + postgres + redis — same shape as `docker-compose.prod.yml`), so login actually works, not just the no-auth gallery. Every credential in the file is a fixed, checked-in, obviously-fake value ("local-dev-only...") rather than a `.env` — nothing there is worth protecting, since no host port is published except via Caddy on `127.0.0.1`. Caddy serves plain `http://localhost` instead of a self-signed cert: Chromium treats `http://localhost` as a secure context, so the Secure-flagged session cookie and the File System Access folder-picker both still work, with no cert-warning click-through needed.
```
cd /home/joakim/code/project/differentiate-pictures-for-auto-sync
docker compose up -d
```
Open `http://localhost:8420`. Photos are read read-only from the real `/home/joakim/Pictures/mammas_bilder` library (same path as production) — this app never writes back into `/photos`, only copies out on download. Stop with `docker compose down`.

First boot has no accounts yet — create the project's two real accounts (see `photo-server/README.md`'s "Two accounts only" rule) directly against the local auth container, once, interactively so the password is never written to a file:
```
docker compose exec auth python -m scripts.create_account --email joakim.reuterborg@gmail.com --role admin
docker compose exec auth python -m scripts.create_account --email elisabeth.reuterborg@gmail.com --role member
```
Accounts persist in the `postgres_data` named volume across `docker compose down`/`up` (only `docker compose down -v` would wipe them).

**Tests**: `.venv-test/bin/python -m pytest app/tests/ -q` (58 tests as of this writing — tree scanning, thumbnails, path-traversal guards, session auth gating, the file-type summary's content-sniffing and its interaction with /api/tree, voiceover upload/list/playback). These run in-process (FastAPI `TestClient`) and don't exercise the browser/DOM at all.

Real browser behavior (album switching, anything DOM/JS-driven) is covered separately by a Selenium suite, since this app has no build step or JS test runner of its own:
```
scripts/test_selenium.sh up                          # disposable Chrome container
.venv-test/bin/python -m pytest app/tests_selenium -q  # starts its own uvicorn + test photo tree
scripts/test_selenium.sh down
```
See `app/tests_selenium/conftest.py` for how the test server/browser are wired together (`--network host` so the containerized browser can reach the host-run uvicorn process).

### Suspending or shutting down the host machine

Checklist before the host machine sleeps/suspends or powers off while this app might be in use:

1. **Check nobody's mid-download** — a burst of recent `/original` requests in the analytics log means an active bulk download; wait for it or warn whoever's downloading first (interrupting it is safe per the cancel/retry handling, but still better avoided).
2. **`git status`** — this project commits continuously, so this should already be clean; if not, commit before stepping away.
3. **`docker compose down`** — stop the container rather than leaving it listening through a suspend/resume cycle. Matches the household's standing rule that nothing should silently start listening again without a human consciously starting it (e.g. after waking on a different, untrusted network).
4. **On resume**: `docker compose up -d` from the repo root brings it back at the same URL.

Suspend (unlike a full shutdown) technically preserves a running container's state through the sleep, so step 3 isn't strictly required for correctness — it's done anyway for the silent-relisten reason above.

## Features (current state)

- **Album view**: grouped by top-level source folder (headline) and immediate parent folder (chunk) — e.g. headline `Florida1`, chunks `Florida1/Florida/1`, `Florida1/Florida/2`. Only one album's DOM (and its thumbnail `<img>` tags) is ever built at all — switching albums via the sticky pill bar tears down the previous album's markup and builds the new one (`renderActiveAlbum()` in `app.js`), rather than keeping every album in the DOM and hiding the rest with CSS, so a hidden album costs no memory or thumbnail requests. The choice persists across reloads via `localStorage`. Toolbar + pill bar are one shared sticky header (`#stickyHeader`), not two independently-positioned sticky elements, so the pill bar can't drift out of sync with the toolbar's real height while scrolling.
- **Thumbnail + fullscreen modes**: click a thumbnail for a fullscreen lightbox with prev/next (also `←`/`→`, `Alt+←` to go back to the grid, `Esc` to close). Grid density toggle (compact/large thumbnails).
- **Media, not just pictures**: pictures (jpg/png/gif/bmp/tif/webp), video (avi and friends), and PDFs are all treated as first-class media and shown/downloaded together. Non-picture media get a generic (non-branded) placeholder thumbnail with the filename burned in, since a thumbnail can't visually preview a PDF or video. Program/installer files (exe, dll, etc.) are deliberately excluded — this app only ever handles media.
- **Downloads — moved into a "⋮ Fler alternativ" menu, 2026-08-05**: no longer front-and-center now that tagging is the main workflow (Joakim's own call, live). The gallery still opens directly, no upfront folder-choice screen; the folder-status label stays in the main toolbar (click anytime to pick/change the save folder — File System Access API, Chrome/Edge only, Firefox/decline falls back to normal per-file browser downloads). "Markera bilder" (multi-select) and "Ladda ner all media" (download-everything) now live behind the toolbar's three-dot button. Single-image download from the lightbox, multi-select-and-download, or download-everything all still go through the same sequential, cancellable, per-file transfer (not a zip - see TODO.md's zip→sequential history).
- **File-type summary**: a button that scans every file in the source folder (not just recognized media) and reports real content-sniffed type per file, flagging any extension/content mismatch. See [../file-integrity/README.md](../file-integrity/README.md) for the full apparatus this is part of.
- **Voiceover narration**: record audio while freely browsing photos, play it back with the right photo and a pointer dot re-appearing in sync with the narration. See [voiceover/README.md](voiceover/README.md).
- **Dismissable info messages**: first-use explanations (e.g. how voiceover recording works) can be permanently dismissed via a "don't show again" checkbox, but stay reachable afterward via the toolbar's "Hjälp" button (Material Symbols `help` icon as of 2026-08-05, was a raw ❓ emoji) — nothing read-once is ever permanently lost. The lightbox carries its own copy of this button (`lbHelpBtn`, top-left, same `help` icon) plus a separate `info`-icon "Bildinformation" button next to it, showing the current photo's filename and full tag list as plain text — useful when boxes/chips on the image itself are hard to parse visually.
- **Activity logging**: every request and a set of semantic UI events (marks, downloads, mode toggles, voiceover start/stop, etc.) are logged to a SQLite database (`/data/analytics.db` in its own docker volume) for later usage analysis.
- **Tags — built 2026-08-05, reworked same day after live use**: a narrowed, build-ready slice of [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s full 12-category design (people/places/objects/animals/occasion + a free-text catch-all; the remaining 7 categories are out of scope for now). Own SQLite table (`tags`, in the same analytics DB), keyed by photo path + user rather than a Postgres `photo_id` this app has no catalog for — see [../tags/SCHEMA.md](../tags/SCHEMA.md)'s "Now (app/'s lightweight build)" section for why and how this differs from the fuller Postgres design. In the lightbox: a "Tagga" button adds a whole-photo tag (e.g. place = "the beach"); a separate "▭ Rita ruta" button arms an explicit box-drawing tool — drag on the photo to draw a region (e.g. a person = "mother"), then adjust it (drag its body to move, its corners to resize) before confirming into the same tag-details form. **Deliberately not an always-on drag** (reworked from the first version, same day): dragging with the tool unarmed does nothing, both because that's what was directly asked for and because an always-on drag would hijack scrolling/pinch gestures on a touch device; mouse and touch are both supported throughout. A too-small initial drag now keeps the tool armed for another attempt instead of silently discarding it with no feedback (the first version's actual reported failure — "didn't stick"). Existing tags render as chips (whole-photo) or boxes-with-labels (bounding-box) overlaid on the image, click any to edit or delete. Value autocompletes against the user's own past tags in that category (`GET /api/tags/values`) — a lightweight stand-in for the full design's `entities` table. Selecting the "Person" category shows an inline tip recommending a tight, face-only box (best practice for both identity-matching embeddings and a future face-blur privacy tool), though nothing enforces it — a manual box can be any size. Every tag row carries a `source` column (`manual` today; `auto` is a reserved value for the automatic-tagging work planned for the next session — nothing produces it yet, but the display/edit UI already renders it distinctly, subtler/dashed, per [../tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s "subtle, concealable" rule for detector-sourced boxes).

## Known limitations

- Auth state and what's still open: [../policies/AUTHENTICATION.md](../policies/AUTHENTICATION.md).
- The File System Access folder-picker only works in Chromium browsers.
