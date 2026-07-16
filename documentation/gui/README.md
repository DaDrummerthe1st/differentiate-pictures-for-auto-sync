# documentation/gui/

The photo-server GUI's first working version — code name `mamma-photo-viewer`,
built 2026-07-16. Despite prior GUI planning existing elsewhere in this repo
(`documentation/photo-server/MOCKUP.md` and its TODO's GUI-coverage items),
this is the first version that actually runs, so **this is the leading
source for how the GUI is supposed to work** — treat those earlier planning
docs as superseded where they conflict with what's built and documented here.

Code lives at the repo root on the `mamma-photo-viewer` branch (`app/`,
`Dockerfile`, `docker-compose.yml`, `requirements.txt`) rather than under a
subdirectory, since it started as a separate repo before ending up here (see
TODO.md's history note). Root `README.md` is a one-line stub pointing back
here, per this repo's doc-layout convention.

## What it is

Single-container, no-login web app for browsing a photo library and picking
files to keep. Built for Joakim's mum to browse `mammas_bilder` (thousands
of family photos) and download the ones she wants — but the underlying
mechanics (album grouping, media-type handling, bulk download, in-picture
voice narration) are meant to generalize to the real photo-server GUI, not
stay one-off.

**Stack**: FastAPI + vanilla JS (no frontend framework, no build step),
single Docker container, self-signed HTTPS (required — the folder-picker
and microphone features both need a secure browser context, which plain
HTTP outside `localhost` doesn't satisfy).

**Run it**:
```
cd /home/joakim/code/project/differentiate-pictures-for-auto-sync
docker compose up -d
```
Open `https://<host LAN IP>:8420`. First load shows a self-signed-cert
warning — click through, that's expected. Stop with `docker compose down`.

**Tests**: `.venv-test/bin/python -m pytest app/tests/ -q` (24 tests as of
this writing — tree scanning, thumbnails, path-traversal guards, zip/download
endpoints, the file-type summary's content-sniffing and its interaction
with /api/tree, voiceover upload/list/playback).

### Suspending or shutting down the host machine

Checklist before the host machine sleeps/suspends or powers off while this
app might be in use:

1. **Check nobody's mid-download** — a burst of recent `/original` requests
   in the analytics log means an active bulk download; wait for it or warn
   whoever's downloading first (interrupting it is safe per the cancel/retry
   handling, but still better avoided).
2. **`git status`** — this project commits continuously, so this should
   already be clean; if not, commit before stepping away.
3. **`docker compose down`** — stop the container rather than leaving it
   listening through a suspend/resume cycle. Matches the household's
   standing rule that nothing should silently start listening again
   without a human consciously starting it (e.g. after waking on a
   different, untrusted network).
4. **On resume**: `docker compose up -d` from the repo root brings it back
   at the same URL.

Suspend (unlike a full shutdown) technically preserves a running
container's state through the sleep, so step 3 isn't strictly required
for correctness — it's done anyway for the silent-relisten reason above.

## Features (current state)

- **Album view**: grouped by top-level source folder (headline) and
  immediate parent folder (chunk) — e.g. headline `Florida1`, chunks
  `Florida1/Florida/1`, `Florida1/Florida/2`. Per-album collapse, a
  "mark as done"/visited toggle with a running counter, and a sticky
  jump-to-album nav bar.
- **Thumbnail + fullscreen modes**: click a thumbnail for a fullscreen
  lightbox with prev/next (also `←`/`→`, `Alt+←` to go back to the grid,
  `Esc` to close). Grid density toggle (compact/large thumbnails).
- **Media, not just pictures**: pictures (jpg/png/gif/bmp/tif/webp), video
  (avi and friends), and PDFs are all treated as first-class media and
  shown/downloaded together. Non-picture media get a generic (non-branded)
  placeholder thumbnail with the filename burned in, since a thumbnail
  can't visually preview a PDF or video. Program/installer files (exe, dll,
  etc.) are deliberately excluded — this app only ever handles media.
- **Downloads**: a one-time folder picker (File System Access API, Chrome/
  Edge only — Firefox falls back to normal browser downloads, no picker)
  writes files straight to a chosen folder with no per-file save dialogs.
  Single-image download from the lightbox, multi-select-and-download from
  the grid, or download-everything — all go through the same sequential,
  cancellable, per-file transfer (not a zip - see TODO.md's zip→sequential
  history if that choice ever needs revisiting).
- **File-type summary**: a button that scans every file in the source
  folder (not just recognized media) and reports real content-sniffed
  type per file, flagging any extension/content mismatch. See
  [../file-integrity/README.md](../file-integrity/README.md) for the
  full apparatus this is part of.
- **Voiceover narration**: record audio while freely browsing photos,
  play it back with the right photo and a pointer dot re-appearing in
  sync with the narration. See
  [voiceover/README.md](voiceover/README.md).
- **Dismissable info messages**: first-use explanations (e.g. how
  voiceover recording works) can be permanently dismissed via a "don't
  show again" checkbox, but stay reachable afterward via the "❓ Hjälp"
  button — nothing read-once is ever permanently lost.
- **Activity logging**: every request and a set of semantic UI events
  (marks, downloads, mode toggles, voiceover start/stop, etc.) are logged
  to a SQLite database (`/data/analytics.db` in its own docker volume) for
  later usage analysis.

## Known limitations

- No auth — LAN-only by design; see TODO.md for the planned login phase.
- Self-signed cert triggers one browser warning on first visit; needs a
  real reverse-proxy cert once this leaves the LAN.
- The File System Access folder-picker only works in Chromium browsers.
