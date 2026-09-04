# test_main.py X BadAlloc rendering 100 photos at once

Status: **confirmed resolved 2026-09-04** — Joakim re-ran `modules/test_main.py` against the
real 100-photo `resources/test_pictures/` folder on his own machine (with a real X display,
which the session that applied the fix didn't have) and the `BadAlloc` crash did not recur.

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

## Security analysis

The fix only changes how many `ImageTk.PhotoImage` widgets `_show_results()` builds and keeps
alive at once (paginated to `IMAGES_PER_PAGE=20`, with old-page widgets destroyed before the
next page renders) — it touches no data handling, no file I/O beyond what was already there
(the same folder Joakim picks via the existing tkinter folder dialog), no network path, and no
privilege boundary. `modules/test_main.py` is explicitly a local-only manual dev tool, never
deployed or exposed. The attack surface is unchanged: the fix reduces memory/pixmap pressure
on the X server, which closes the resource-exhaustion path this bug describes (a large enough
folder could always have retriggered the same `BadAlloc` before this fix, effectively a local,
unintentional self-inflicted DoS against the developer's own X session, not an externally
exploitable one). No residual risk identified — `IMAGES_PER_PAGE=20` bounds memory regardless
of folder size, so the same crash class can't recur at any folder size larger than 100.
