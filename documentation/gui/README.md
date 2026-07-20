# documentation/gui/

The photo-server GUI's first working version — code name `mamma-photo-viewer`, built 2026-07-16. Despite prior GUI planning existing elsewhere in this repo (`documentation/photo-server/MOCKUP.md` and its TODO's GUI-coverage items), this is the first version that actually runs, so **this is the leading source for how the GUI is supposed to work** — treat those earlier planning docs as superseded where they conflict with what's built and documented here.

Code lives at the repo root on the `mamma-photo-viewer` branch (`app/`, `Dockerfile`, `docker-compose.yml`, `requirements.txt`) rather than under a subdirectory, since it started as a separate repo before ending up here (see TODO.md's history note). Root `README.md` carries the normal project pitch plus a section pointing back here for this branch's work.

## What it is

Single-container, no-login web app for browsing a photo library and picking files to keep. Built for Joakim's mum to browse `mammas_bilder` (thousands of family photos) and download the ones she wants — but the underlying mechanics (album grouping, media-type handling, bulk download, in-picture voice narration) are meant to generalize to the real photo-server GUI, not stay one-off.

**Stack**: FastAPI + vanilla JS (no frontend framework, no build step), single Docker container, self-signed HTTPS (required — the folder-picker and microphone features both need a secure browser context, which plain HTTP outside `localhost` doesn't satisfy).

**Run it — currently broken on this dev workstation, read before running**: as of 2026-07-19 the repo-root `docker-compose.yml` is stale — it predates `app/auth.py`'s login requirement and has no `JWT_SECRET_KEY` set, so the command below crashes at startup (`MissingConfigError`). No local full-stack dev environment exists yet; the only live deployment is production (`https://photos.reuterborg.se`, see `DEPLOYMENT.md`). See `TODO.md`'s 2026-07-19 section before relying on this locally. The command below is what runs it once that's fixed:
```
cd /home/joakim/code/project/differentiate-pictures-for-auto-sync
docker compose up -d
```
Open `https://<host LAN IP>:8420`. First load shows a self-signed-cert warning — click through, that's expected. Stop with `docker compose down`.

**Tests**: `.venv-test/bin/python -m pytest app/tests/ -q` (53 tests as of this writing — tree scanning, thumbnails, path-traversal guards, session auth gating, the file-type summary's content-sniffing and its interaction with /api/tree, voiceover upload/list/playback). These run in-process (FastAPI `TestClient`) and don't exercise the browser/DOM at all.

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

- **Album view**: grouped by top-level source folder (headline) and immediate parent folder (chunk) — e.g. headline `Florida1`, chunks `Florida1/Florida/1`, `Florida1/Florida/2`. Only one album's DOM (and its thumbnail `<img>` tags) is ever built at all — switching albums via the sticky pill bar tears down the previous album's markup and builds the new one (`renderActiveAlbum()` in `app.js`), rather than keeping every album in the DOM and hiding the rest with CSS, so a hidden album costs no memory or thumbnail requests. The choice persists across reloads via `localStorage`. Toolbar + pill bar are one shared sticky header (`#stickyHeader`), not two independently-positioned sticky elements, so the pill bar can't drift out of sync with the toolbar's real height while scrolling. (Per-album collapse and a "mark as done" toggle existed briefly here and were removed 2026-07-19 — see TODO.md — once only one album was ever shown at a time, their original purpose from the old all-albums-stacked layout no longer applied.)
- **Thumbnail + fullscreen modes**: click a thumbnail for a fullscreen lightbox with prev/next (also `←`/`→`, `Alt+←` to go back to the grid, `Esc` to close). Grid density toggle (compact/large thumbnails).
- **Media, not just pictures**: pictures (jpg/png/gif/bmp/tif/webp), video (avi and friends), and PDFs are all treated as first-class media and shown/downloaded together. Non-picture media get a generic (non-branded) placeholder thumbnail with the filename burned in, since a thumbnail can't visually preview a PDF or video. Program/installer files (exe, dll, etc.) are deliberately excluded — this app only ever handles media.
- **Downloads**: the gallery opens directly, no upfront folder-choice screen. On the first download action of any kind (lightbox, multi-select, or download-everything), the app offers a folder picker (File System Access API, Chrome/Edge only — Firefox and any decline/cancel just fall back to normal per-file browser downloads, no nagging on later downloads). The toolbar's folder-status label doubles as a button — click it anytime to pick or change the folder; hover shows the folder's own name (the browser API never exposes a full filesystem path, by design). Single-image download from the lightbox, multi-select-and-download from the grid, or download-everything — all go through the same sequential, cancellable, per-file transfer (not a zip - see TODO.md's zip→sequential history if that choice ever needs revisiting).
- **File-type summary**: a button that scans every file in the source folder (not just recognized media) and reports real content-sniffed type per file, flagging any extension/content mismatch. See [../file-integrity/README.md](../file-integrity/README.md) for the full apparatus this is part of.
- **Voiceover narration**: record audio while freely browsing photos, play it back with the right photo and a pointer dot re-appearing in sync with the narration. See [voiceover/README.md](voiceover/README.md).
- **Dismissable info messages**: first-use explanations (e.g. how voiceover recording works) can be permanently dismissed via a "don't show again" checkbox, but stay reachable afterward via the "❓ Hjälp" button — nothing read-once is ever permanently lost.
- **Activity logging**: every request and a set of semantic UI events (marks, downloads, mode toggles, voiceover start/stop, etc.) are logged to a SQLite database (`/data/analytics.db` in its own docker volume) for later usage analysis.

## Known limitations

- No auth — LAN-only by design; see TODO.md for the planned login phase.
- Self-signed cert triggers one browser warning on first visit; needs a real reverse-proxy cert once this leaves the LAN.
- The File System Access folder-picker only works in Chromium browsers.
