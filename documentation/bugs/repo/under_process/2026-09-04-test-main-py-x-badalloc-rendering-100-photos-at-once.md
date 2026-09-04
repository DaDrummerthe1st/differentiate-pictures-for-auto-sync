# test_main.py X BadAlloc rendering 100 photos at once

Status: **fix applied, not yet confirmed** — per this folder's own rule (README.md: "not
mitigated, not 'probably fine now,' genuinely confirmed resolved"), this stays in
`under_process/` until Joakim confirms the paginated version actually stops crashing against
his real 100-photo folder - the session that applied the fix had no display to verify the
X-rendering path itself against, only that the logic still imports and modules/tests/ still
pass.

## Symptom

Joakim pointed `modules/test_main.py` at a real 100-photo sample
(`resources/test_pictures/`, populated via `tools/sample_test_pictures.sh`) and got:

```
X Error:  BadAlloc
  Request Major code 53 ()
  Error Serial #17096
  Current Serial #17178
```

The process exited; no results window stayed open.

## Investigation log

1. `_show_results()`'s original implementation looped over every path in the folder,
   building one `ImageTk.PhotoImage` per photo (each resized to `MAX_DISPLAY_WIDTH=900`px, so
   still hundreds of KB to a few MB of raw pixel data each) and packing all of them into one
   scrollable `Frame`, keeping every `PhotoImage` alive in a single `photo_refs` list for the
   life of the window.
2. `BadAlloc` (X11 error code, major opcode 53 = `CreatePixmap`) is the X server refusing a
   pixmap allocation request - not a Python-level OOM, a server-side resource limit. 100
   simultaneous ~900px-wide RGB images is easily 250-350MB of pixmap data requested from the X
   server in one session, on top of whatever else was already using X server memory.
3. Confirmed the counting: with `MAX_DISPLAY_WIDTH=900`, a typical 3:4 phone photo scales to
   roughly 900x1200px RGB = ~3.2MB per rendered `PhotoImage`; 100 of them = ~320MB, all held
   live simultaneously with no ceiling - this scales linearly and unboundedly with folder size,
   so any large-enough folder would eventually hit this regardless of exact photo dimensions.

## Root cause

`_show_results()` had no limit on how many fully-rendered photos it kept alive at once - it
scaled linearly with folder size, with no ceiling.

## Fix

Paginated `modules/test_main.py`: `IMAGES_PER_PAGE = 20` per page, with Prev/Next navigation.
Changing page destroys every widget (and drops every `PhotoImage` reference) from the current
page before building the next, so memory stays bounded to one page's worth regardless of how
many photos the folder holds. Verified: `modules/tests/` (24 tests) still pass, module imports
cleanly; the actual X-server-bound rendering path can only be verified by running it with a
real display, which this session's sandbox doesn't have - Joakim to confirm on his machine.

## What changed

`modules/test_main.py`'s `_show_results()` now paginates instead of rendering an entire folder
at once - see `IMAGES_PER_PAGE`'s comment there for the reasoning, and
`modules/README.md`/`documentation/GLOSSARY.md` (BadAlloc entry) for the write-up.

## Next session should start with

Confirm with Joakim whether re-running `modules/test_main.py` against the real 100-photo
`resources/test_pictures/` folder now works without crashing. If yes, run
`tools/create_bug_report/mark_solved.sh 2026-09-04-test-main-py-x-badalloc-rendering-100-photos-at-once.md`
to close this out (that step also requires appending the `## Security analysis` section this
folder's README.md requires on every move to `fixed/`). If it still crashes (e.g. `IMAGES_PER_PAGE=20`
is still too many for his X server, or the crash was something else entirely), lower
`IMAGES_PER_PAGE` first as the cheapest next lever before re-investigating from scratch.
