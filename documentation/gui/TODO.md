# TODO — documentation/gui/

## Login/authentication

Current state, architecture (why `app/` verifies `server/`'s tokens rather than implementing its own auth), remaining hardening priority, and the OAuth-exclusion decision all moved to [../policies/AUTHENTICATION.md](../policies/AUTHENTICATION.md) 2026-07-23 — project-wide topic (applies to `server/`'s auth backend too, not just this app), single source of truth there, not restated here.

**Branch state, resolved**: `phase-1-login` and `master` were merged into `mamma-photo-viewer` on 2026-07-21 (history preserved, `--allow-unrelated-histories`, 33 conflicts resolved — see CHANGELOG_ARCHIVE.md's 2026-07-21 entry). **Fully closed 2026-08-05**: `mamma-photo-viewer`, `mamma-photo-viewer-folder-ux`, and `phase-1-login` were confirmed as pure ancestors of `master` (nothing left to merge), run through the merge routine as a formality, and deleted (local + remote) — `master` is now the only branch, so there's no more "catch this branch up" relationship to track.

## Voiceover feature

Moved to its own subfolder: [voiceover/README.md](voiceover/README.md) (how it works today) and [voiceover/TODO.md](voiceover/TODO.md) (the planned MP4-export work) — substantial enough a feature to warrant its own doc root rather than living inline here.

## History note: why this project lives in this repo at all

Started as a genuinely separate repo (`~/code/project/mamma-photo-viewer`), but an accidental concurrent Claude Code session fetched that repo's history into this one under a same-named branch. **Corrected 2026-07-19**: originally attributed to a suspected VS Code extension bug (typing while a popup was opening); the actual cause, identified by Joakim, is that editing/changing a previously-sent prompt forks the conversation into a new tab - expected behavior, not a bug, that only looked alarming because both tabs' sessions shared this same working tree. Once discovered, Joakim opted to keep building here rather than untangle it back out.

## History note: why bulk downloads are sequential, not a zip

Originally "download all"/"download selected" built one zip server-side, then streamed it. Switched away from this 2026-07-16 after mum's actual download over real (slow, USB-drive-destination) conditions showed the real problems: a single zip is all-or-nothing (any interruption loses the whole batch), gives no real progress feedback until fully built, and can't be cancelled cleanly. Per-file sequential transfer (now used by both buttons) shows honest incremental progress, survives individual file failures, and can be cancelled without losing anything already saved. Confirmed as a permanent decision (not just a workaround) the same day - the zip endpoint (`POST /api/zip`), its client-side code, and its tests were removed entirely rather than left dormant.

## Analytics log format — more narrative, less terse

Idea floated by Joakim 2026-07-17, not decided or started: today's `_log_event()` rows are terse structured fields (event type + a short detail string, e.g. `download_zip_done count=12`). Over many iterations of this app, terse IDs stop being legible on their own (`"#12345 opened by #22345 zoomed in"`). Direction being considered: freetext-style log lines that stay self-explanatory read cold, e.g. `"User #12345 opened picture #2344554 and spent 234 secs zooming and pressing buttons"`. Trade-off not yet weighed: more legible over time vs. harder to query/aggregate than structured fields. Needs a design decision (keep structured fields and add a rendered freetext view, or replace the stored format outright) before any implementation — TDD applies as usual once decided.

## Open from the 2026-07-18 session

- **Download-folder UX rework — built 2026-07-20** on branch `mamma-photo-viewer-folder-ux`: the upfront `#setup` "choose folder" screen (blocking first use) is gone — the gallery now shows immediately on load. A folder is instead offered lazily via `maybeOfferFolderPicker()` in `saveImage()`, the first time *any* save action happens (single lightbox download or bulk); declining/cancelling or the browser not supporting `showDirectoryPicker` is remembered forever (`localStorage`'s `mpv_folder_prompt_done`) so it never nags again — re-picking afterward only happens by clicking the toolbar's `downloadFolderLabel`, now a real `<button>`. **Deviation from the original design note**: "hoverable to show the full path" turned out to not be implementable — confirmed via MDN/Chrome docs that `FileSystemDirectoryHandle` only ever exposes the picked folder's own `.name`, never a full OS path (deliberate browser privacy sandboxing, no `resolve()` workaround since that needs a known ancestor handle). The hover title shows the folder name instead. Covered by `app/tests_selenium/test_folder_prompt.py` (5 new tests: no setup screen, default label text, click-to-repick, lazy-offer-once, decline-remembered-across-reload); `conftest.py` and three existing Selenium tests that used to click the removed `skipFolderBtn` were updated to match.
- **Decided 2026-07-18: Selenium, not Playwright** — per `POLICY.md`'s new vendor-lock-in-and-openness principle (prefer vendor-neutral tools; Playwright is Microsoft-driven, Selenium is a W3C standard with no single owner). Selenium's usual downsides (verbose API, historically flakier waits) matter less here than usual: this app's test surface is small, and the File System Access API it depends on is Chromium-only anyway (Firefox already gets a documented fallback), so there's no real cross-browser-coverage benefit from Playwright being given up. Containerized only (`POLICY.md`'s no-system-installs rule) - `selenium/standalone-chrome` is the equivalent of the Playwright image previously considered. **Built 2026-07-19** (first real payoff of this decision): see `scripts/test_selenium.sh` and `app/tests_selenium/` — used for the single-album-view switching tests below.
- **Thumbnail pre-compile — shelved 2026-07-20** - see `../bugs/repo/under_process/2026-07-17-pre-compile-thumbnails-ahead-of-time.md`'s "Shelved" section: an investigation into three added requirements (cache location, delete-flag cleanup, multi-user readiness) surfaced real open forks in all three; Joakim opted to wait for the incoming RAM upgrade instead of building now.
- **Grid pagination**, a separate/complementary idea to pre-compiling - see `../bugs/repo/under_process/2026-07-18-paginate-the-grid-instead-of-loading-all-thumbnails-at-once.md`. Candidate, not evaluated.
- **Lightbox bug, not root-caused** - see `../bugs/repo/under_process/2026-07-18-lightbox-shows-previous-photo-when-clicking-a-not-yet-loaded-thumbnail.md`. Symptom changed after today's redeploy (now shows nothing instead of the previous photo) - needs a live repro with DevTools open, not more static code reading.
- **New, 2026-07-20: thumbnails load bottom-first in a large album** - see `../bugs/repo/under_process/2026-07-20-ishotellet-album-thumbnails-load-bottom-first-instead-of-top-first.md`. Confirmed on the "Ishotellet" album (354 files, 718M); leading theory is native `loading="lazy"` interacting unexpectedly with a large album's layout - needs a live DevTools repro, not chased down yet.

## 2026-07-19 session: single-album view, and a local-dev gap found along the way

- **Done**: only one album renders at a time now; the nav-pill bar switches which one (`setActiveAlbum()` in `app.js`), persisted across reloads via `localStorage` (`mpv_active_headline`). Covered by the new Selenium suite (`app/tests_selenium/test_album_switching.py`) - see the Selenium bullet above.
- **Not changed, flagged for a future decision**: "download all" and the lightbox's prev/next still span every album, including hidden ones (`allImages` in `app.js` is still built from every section, not just the active one) - this was already the case before today and is preserved as-is, not addressed by this session. Worth a deliberate decision later (scope both to the active album only? keep global?), not a silent behavior change to make alongside the display switch.
- **Found, not this session's scope to fix**: the root `docker-compose.yml` (this repo's own dev machine, not the production server) is stale relative to `app/auth.py` — it predates the 2026-07-17 P0 commit (`9c090b0`) that made the app require a `JWT_SECRET_KEY` env var (and, in production, a running `auth`/postgres/redis stack) just to start. The one container that ever ran here did so for a few hours on 2026-07-16, before that commit, and has sat `Exited` ever since - it was never evidence of an ongoing local workflow. The actual live system is production only, kept current by push-here/pull-and-rebuild on the server (`192.168.1.10`, `docker-compose.prod.yml`) - confirmed reachable and current as of 2026-07-19. A rebuild of the root `docker-compose.yml` as it stands today would fail at startup (`MissingConfigError`). No local full-stack dev environment (photo-viewer + auth + postgres + redis, reachable in a browser on this workstation) exists today; this session's new Selenium suite works around that by running `uvicorn` directly against a disposable test photo tree with a fixed `JWT_SECRET_KEY`; it doesn't fix or replace the stale root compose file itself. **Fixed 2026-07-23** — see [README.md](README.md)'s "Run it" section and CHANGELOG_ARCHIVE.md's 2026-07-23 entry.
- **Follow-up fix, same day, after production feedback with Joakim's real 16-album library**: two real bugs the 3-fake-album local test hadn't caught. (1) The single-album view above only hid inactive albums with CSS (`display: none`) - all of them were still fully built into the DOM with real thumbnail `<img>` tags, which Joakim correctly flagged as unnecessary weight at real-library scale (not just a "make it invisible" ask). Fixed: `renderActiveAlbum()` now builds *only* the active album's DOM at all; switching tears it down and rebuilds, confirmed via a new Selenium test asserting the other albums have zero matching DOM nodes, not just a `hidden` class. (2) The toolbar and pill bar were two independently `position: sticky` elements, the pill bar's offset hardcoded to `top: 3.6rem` assuming a toolbar height that didn't match reality (measured 111.78px vs assumed 57.6px on the real page) - scrolling left the pill bar partly covered. Fixed by wrapping both in one `#stickyHeader` container that alone is sticky, so there's no offset to keep in sync at all. Covered by a new Selenium test (`test_sticky_header.py`) asserting no vertical overlap after scrolling, via real `getBoundingClientRect()` geometry, not a visual guess.
- **Bootstrap + jQuery + Material Symbols vendored — 2026-07-21**, on branch `design/icons-and-ui-libs`: the direction raised below (adopting established libraries instead of pure vanilla JS+CSS) is now underway. jQuery 4.0.0 (slim build), Bootstrap 5.3.8 (CSS + JS bundle), and a self-hosted Material Symbols Outlined variable font are vendored under `app/static/vendor/` and linked from `index.html` — no CDN (POLICY.md's closed-by-default rule: a CDN load leaks the viewer's IP and access pattern to the third party on every page load, not just photo data, which was judged unacceptable for this app's actual user), no build step added (still plain `<link>`/`<script>` tags, no bundler/npm toolchain). Bootstrap's built-in Reboot covers the CSS-reset/normalize idea below without a separate library. Confirmed working via a live smoke-check (all vendored assets return 200) plus the existing `app/tests` (53) and `server/tests` (49) suites, both green. Not yet done: actually restyling markup/icons to use these libraries (this step was plumbing only) — that's the next piece of this work. **Reference implementation exists, 2026-07-27**: [prototypes/upload-and-share-mockup/](../../previous-work/multi-user-web-app/prototypes/upload-and-share-mockup/README.md) uses this exact vendored Material Symbols font (copied from `app/static/vendor/`) throughout, including the `<span class="material-symbols-outlined">icon_name</span>` + icon-in-button CSS convention (`prototypes/upload-and-share-mockup/style.css`'s `.material-symbols-outlined`/`.btn`/`.nav-pill`/`.chip` icon-sizing rules) — a working pattern to copy into `app/static/index.html`/`app.js`/`style.css` directly rather than re-deriving icon-button conventions from scratch when this step is actually picked up.
- **Removed entirely, same day**: "Markera som klar" (per-album visited toggle + the toolbar's "X av Y album visade" counter) and "Dölj" (per-album collapse). Joakim didn't remember what either did when asked where their buttons should move to once the header row goes away - on finding out "Dölj" specifically had been designed for the old all-albums-stacked layout (collapsing a reviewed album saved scroll space) and had no clear purpose left now that only one album is ever shown at all, he asked to delete both outright rather than relocate them. Removed from `app.js` (`toggleVisited`, `updateVisitedUI`, `loadSet`/`saveSet`, the `visitedHeadlines`/ `collapsedHeadlines` Sets, the per-album `visitedBtn`/`collapseBtn`/ `headline-actions` markup), `index.html` (`#visitedCounter`), and `style.css` (`.visited-btn`, `.collapse-btn`, `.headline-actions`, `.nav-pill.visited`, `.album-body.collapsed`) - nothing left pointing at the removed feature.
- **Bigger redesign raised, not built**: Joakim wants folder-path segments reframed explicitly as tags/sub-tags (album = tag, dated subfolder = sub-tag) and the per-album `<h2>` header removed entirely
  - "each section of pictures represented by tags, choosable in the now pills section." Genuinely open before building: where do sub-tags live (a second pill row under the active tag? inline chips above the grid? folded into one flat pill list?), and does a sub-tag filter the grid or just scroll to it. Not decided - needs its own design pass, not a guess.
- **Fixed: thumbnails silently breaking on token expiry, without ever needing a reload.** The already-known bug (`../bugs/repo/fixed/2026-07-18-thumbnail-img-tags-have-no-silent-refresh-on-expired-access-token-SOLVED.md`) went from "a mechanism that exists" to confirmed-live during this session - Joakim hit it in normal browsing, no server restart involved. "Just reload" turned out not to be a real workaround either (the File System Access folder permission doesn't reliably survive a reload, bouncing back to the folder-picker screen, plus losing scroll position). Fixed with the standard "silent refresh" pattern (confirmed against external sources, not guessed - see the 2026-07-19 CHANGELOG entry for the citations): `app.js` now runs a proactive timer (`silentRefresh()`, every 4 minutes, safely under the 5-minute access-token expiry) calling `/refresh` in the background the entire time the gallery is open, so the session cookie - which plain `<img src>` thumbnail/lightbox loads rely on entirely, since they can't go through `authFetch`'s reactive retry - never actually goes stale during normal use. `?test_refresh_ms` overrides the interval so the new Selenium test doesn't wait out the real 4 minutes.
- **Follow-up, same day**: Joakim flagged that the fix above has a real side effect - it keeps a session alive forever as long as a tab stays open, even genuinely unattended, with no idle timeout at all. Fixed: `app.js` now tracks real user activity (`mousemove`/`keydown`/`click`/ `scroll`/`touchstart`), and `silentRefresh()` skips the proactive `/refresh` call once 30 minutes have passed with none. This doesn't force an abrupt logout - it just stops artificially extending the session past what the existing 5-minute access-token / 12-hour refresh-token lifetimes already impose, restoring the bound that existed before today's silent-refresh fix. `?test_idle_ms` overrides the threshold for the new Selenium test.

## 2026-08-05 session: tags GUI foundation, ahead of next session's automatic tagging

Built a narrowed, build-ready slice of [../tags/TAXONOMY.md](../tags/TAXONOMY.md)'s design directly
into this app — see [README.md](README.md)'s Tags feature entry and
[../tags/SCHEMA.md](../tags/SCHEMA.md)'s "Now" section for the full technical shape (own SQLite table,
keyed by photo path since there's no Postgres photo catalog yet; 5 categories, not 12; no
entities/relationships). In the lightbox: whole-photo tags via a new "Tagga" button, manual
bounding-box tags by dragging directly on the image, edit/delete any existing tag by clicking its chip
or box, value autocomplete against the user's own past tags per category. `app/tests/test_tags.py` (30
tests) + `app/tests_selenium/test_tag_ui.py` (5 tests) cover it.

**For next session, building automatic tagging**: every tag row already carries a `source` column
(`manual` | `auto`) and the display/edit UI already renders `auto`-sourced tags distinctly (subtler,
dashed border/outline, per [UX_FLOWS.md](../tags/UX_FLOWS.md)'s "subtle, concealable" rule) - nothing
produces `source='auto'` rows yet, since no detector exists. A detector pass should be able to `INSERT`
directly into `app/`'s existing `tags` table (`source='auto'`, its own `bbox_x/y/w/h` if it found a
region) and have it show up in the lightbox with zero GUI changes needed - confirm that assumption
holds before building the detector rather than after.

Also found and fixed, unrelated to the tags work itself but blocking it:
[../bugs/repo/fixed/2026-08-05-selenium-test-harness-readiness-probe-never-succeeds-since-the-app-shell-auth-gate-SOLVED.md](../bugs/repo/fixed/2026-08-05-selenium-test-harness-readiness-probe-never-succeeds-since-the-app-shell-auth-gate-SOLVED.md)
— the entire Selenium suite had been silently broken since the 2026-07-23 auth-gate commit; nobody had
re-run it for real since. Worth running `scripts/test_selenium.sh up && .venv-test/bin/python -m
pytest app/tests_selenium -q` at least once per session that touches `app/static/` or auth gating, not
just assuming it still passes.

## Same-day follow-up: rework driven by live feedback

The first version of the box tool above (an always-on drag directly on the image) shipped, then broke
under real use within the same session — Joakim tried it live on the local dev stack and reported "no
way to actually draw the bounding box." Root causes, both found live rather than guessed at: (1) a
too-small drag was silently discarded (2% of image width as the cutoff, rejected without any visible
feedback) - reported as "if the bounding box i drew was too small, it didn't 'stick'"; (2) drawing an
exact box around a face by hand is genuinely hard on a first attempt with no way to correct it - "most
often I draw too big a container." Also requested directly: "I would prefer a drag a square-tool"
(an explicit tool, not an implicit always-on drag).

**Rebuilt as a real interaction, not a patch**: `#lbDrawBoxBtn` ("▭ Rita ruta") arms an explicit
draw mode (idle → armed → adjusting state machine in `app.js`); dragging with it unarmed does nothing,
on purpose - the same design also fixes touch support for free, since an always-on drag would otherwise
hijack scrolling/pinch gestures on a phone every time a finger touched the photo (mouse and touch event
handlers are now genuinely parallel, not mouse-only). The minimum-drag-size check moved from a
fraction-of-image-width cutoff to a small fixed-pixel one (6px), so a deliberately small face box on a
large photo no longer gets swallowed. After the first drag, the box enters an "adjusting" state with
four corner handles (drag to resize) and a draggable body (drag to move) before confirming into the
tag-details form — directly answers the "too big a container" precision complaint. Also added, same
pass: an `occasion` category (6th, alongside people/places/objects/animals/generic - "I would like to
tag them with peoples names, places occasions etc"), a face-only tip shown under the category picker
when "Person" is selected, and a "⋮ Fler alternativ" menu that moved download/select-mode out of the
main toolbar (Joakim's own call - "no need for the download option at this stage") plus a
`help`/`info`-icon pair on the lightbox (Material Symbols, matching Google/Apple Photos' own
info-panel convention) - the info icon opens a plain-text photo-info modal (filename + full tag list),
a placeholder for the fuller EXIF/date/GPS panel `../photo-server/TODO.md` Phase 4.8 still hasn't built.

**Deferred, explicitly, not forgotten** (Joakim asked to wrap up rather than keep expanding scope
live): splitting `app.js`/`style.css` into real ES modules (`<script type="module">` + `import`/
`export` — see [GLOSSARY.md](../GLOSSARY.md)) was raised for the new tags code specifically and agreed
in principle, but not done this pass to avoid stacking a script-loading change on top of still-being-
written interactive logic; global tag search/browse ("the possibility to see and search for tags") was
raised and not built. See the changelog entry for this session's second commit for the full list handed
to the next session.

## 2026-08-07 session: role-based tag visibility + a detector service skeleton (Phase 0-1 of the automatic-tagging build plan)

Automatic tagging itself (the actual goal named at the start of this session) was scoped down live
to just its first two prerequisite phases — Joakim: "only do phase 0 and 1 in this session. then
leave VERY SHORT notes for me to initialize phase 2 in the next session." Full build plan (roster,
category mappings, all 7 phases) is in this session's plan; only the summary below is duplicated
here.

**Phase 0, done**: tags now have role-based visibility instead of strict per-`user_id` filtering.
Raised directly ("build user groups. elisabeth = user with her own space to save in. joakim = admin
= access everywhere... do not build for these exact users, build user groups") - `server/`'s login/
refresh now mint a JWT carrying a `role` claim (`member`|`admin`), and `app/main.py`'s
`GET /api/tags`/`GET /api/tags/values` use it: a member sees their own manual tags plus every
`source='auto'` tag regardless of who wrote it; an admin sees everything. Write endpoints are
unchanged - this is read-visibility only, not wider edit/delete rights. See
[../tags/SCHEMA.md](../tags/SCHEMA.md)'s "Now" section for the full detail.

**Phase 1, done**: a new `detector/` container (FastAPI, `GET /health` only) now runs alongside
`photo-viewer` in `docker-compose.yml`, internal-network-only (no host port published) - the future
home for the CV/ONNX models themselves, kept out of `photo-viewer`'s own image on purpose ("let the
different models... be containerized and controlled by the main app"). Build + reachability
smoke-tested locally against this workstation's own dev stack, then torn down - nothing left running.

**Deferred to next session, per the saved plan's own Phase 2 handoff**: the actual quality/face/
object detectors, the `auto_tag.py` orchestration job, a local smoke-test against
`resources/test_pictures/` (real, disposable, already local - Joakim asked to test on this
workstation before anything touches the server), and only then written-not-run deploy commands for
the server's `/tank` library. Global tag search/browse and the ES-module split (both raised
2026-08-05) remain untouched, lower priority per the original ask's own ordering.

## Other open items (carried over, not yet done)

- Recheck for anything else possibly missing from the branch-mixup incident referenced above.
- If this app is ever shared/open-sourced, re-check this documentation and the code for personal/family references (paths, filenames, memorial context) that shouldn't be public.
