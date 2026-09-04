# Quality-percent table

Designed, not built. Column shape for a table that would record per-photo quality
scores as continuous percentages, keyed by `file_id` (UUID, FK to a separate files
table) — deliberately decoupled from [tags/SCHEMA.md](../tags/SCHEMA.md)'s `tags`
table and from `detector/quality.py`'s boolean/enum outputs. This is the design
behind [modules/blur_check.py](../../modules/blur_check.py) (currently only
`blur_percent` is implemented; `exposure_percent`/`saturation_percent` are designed
here, not yet coded).

| Column | Range | Low means | High means |
| --- | --- | --- | --- |
| `file_id` | UUID (FK) | — | — |
| `blur_percent` | 0 to 100 | sharp | blurry |
| `exposure_percent` | -100 to +100 | (negative) underexposed | (positive) overexposed, 0 = balanced |
| `saturation_percent` | 0 to 100 | grayscale | colorful |
| `created_at` | timestamp | — | — |

`created_at` follows the same convention already used on `tags`/`entities` in
[tags/SCHEMA.md](../tags/SCHEMA.md) (`id, photo_id, user_id, created_at`) — when the
row was computed, not when the photo was taken (that's EXIF data on the file itself,
a different fact).

## Why these shapes, not the obvious alternatives

- **`exposure_percent` is one signed column, not two (`underexposed_percent` +
  `overexposed_percent`)**: mean luminance is a single axis (0=black, 255=white),
  so the two would be mutually exclusive — only one is ever non-zero for a given
  photo, making the other permanently dead weight on every row. A signed column
  carries the same information with no redundancy, and mirrors a convention people
  already know: camera exposure compensation (EV), shown on every camera/phone
  camera app as a +/- dial — negative darker, positive brighter, 0 balanced.
- **`saturation_percent`, not `black_and_white_percent`**: `black_and_white_percent`
  frames grayscale as a defect, but black-and-white is frequently an intentional
  creative choice, not a flaw the way blur/bad exposure are — a neutral measurement
  name fits better than a "problem percent" one. `saturation` is also the actual
  colorimetry term (the S in HSV/HSL), already familiar from every photo editor's
  saturation slider, so which end is "more color" needs no legend.
- **`blur_percent` unchanged**: no shorter/better-known synonym fits — "blur" is
  already the standard term, and unlike exposure/saturation it's one-directional
  (only one way to be bad), so it never had the two-columns-or-sign-convention
  problem the others did.

Trade-off accepted: unlike `blur_percent`/`exposure_percent` (high = worse),
`saturation_percent` reads the opposite way (high = more color, generally neutral-to-
good). No uniform "high always means bad" rule across the table — each column uses
its own domain-standard direction instead of an artificial shared one.

## Status

Designed 2026-09-04, in conversation — not yet implemented beyond `blur_percent` in
`modules/blur_check.py`. See [TODO.md](TODO.md).
