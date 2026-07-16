# documentation/file-integrity/

The apparatus for detecting files that aren't what they claim to be —
covers both innocent mishaps (decades-old photo collections copied across
many backup media accumulate real corruption) and the security angle
(a mismatched extension is a classic way to disguise a malicious file).
Built for [documentation/gui/](../gui/README.md) (`mamma-photo-viewer`),
but the approach is meant to generalize to the rest of the photo-server
work in this repo wherever files of uncertain origin get handled.

## What it actually does

Every file's *real* type is determined by reading its first bytes and
matching known magic numbers (`app/main.py`'s `_sniff_file_type`) —
JPEG/PNG/GIF/BMP/TIFF/WEBP, PDF, RIFF-based AVI/WEBP, MP4/QuickTime's
`ftyp` box, Windows PE binaries (`MZ`), ZIP and CAB archives, with a
printable-ASCII heuristic for plain text and an "unknown binary" catch-all
for everything else. This is compared against what the *extension*
implies (`_EXPECTED_LABEL_FOR_EXT`) for the media types this app cares
about (pictures, video, PDF).

**Where this shows up:**
- `GET /api/file-summary` scans every file under the photo root
  (regardless of extension), returns a total count, a category
  breakdown by *detected* type, and a list of every extension/content
  mismatch found. Exposed in the GUI via a summary button (per Joakim's
  request: intuitive, one click, shows the full breakdown "all the way
  down to the first few bytes"). Confirmed cheap: ~0.5s for 3,444 files.
- `GET /api/tree` (the browsable/thumbnailable listing) excludes any
  file with a mismatch — it's never shown as if it were a real photo.
  It's still fully visible via `/api/file-summary`, per the "don't hide
  it, just don't present it as trustworthy" requirement.
- `GET /thumb` additionally falls back to a placeholder for any
  picture-extension file that *passes* the mismatch check (header looks
  right) but still fails to actually decode - a corruption case the
  header-only sniff can't catch, only Pillow's real decoder can.

**Real result:** running this against the actual `mammas_bilder`
library found 4 genuinely corrupted `.JPG` files (valid-looking
filename, not valid JPEG content) that had been silently present in the
library, presumably from being copied across old backup media over the
years.

## What this is *not*

This is content-*type* verification, not a virus scanner. It answers
"does this file's content match what its name claims" - a necessary but
nowhere near sufficient signal for malware. A `.jpg` that is genuinely,
correctly, a JPEG can still carry a malicious payload via a decoder
exploit; this apparatus would never catch that. If real malware scanning
is ever needed (see TODO.md - it will be, once uploads exist), that's a
distinct capability (e.g. ClamAV or a cloud AV API) layered on top of
this, not a replacement for it.

## Limits of the current sniffing

- Magic-number coverage is deliberately scoped to the types this app
  actually serves (pictures, PDF, the video extensions with static
  RIFF/`ftyp` signatures). `.mkv`/`.webm` are accepted by extension but
  have no signature check yet (EBML-based, different magic bytes) - see
  TODO.md.
- The "Textfil" / "Okänd binärfil" buckets are broad catch-alls, not an
  exhaustive format library - this system is a practical heuristic, not
  a forensic file-identification tool.
- A mismatched file is left exactly where it is on disk, just excluded
  from the browsable listing - this is not a quarantine mechanism (see
  TODO.md).
