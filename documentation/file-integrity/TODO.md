# TODO — documentation/file-integrity/

## Treat upload-time mismatches as a security signal, not just a mishap

Today, an extension/content mismatch in `mammas_bilder` is almost
certainly innocent - old files that got corrupted or mislabeled across
years of copying between backup media. That assumption stops being safe
the moment users can upload their own files (see
[documentation/gui/TODO.md](../gui/TODO.md)'s login/auth phase - "her"
there is not necessarily Joakim's mum; multi-user upload is the
eventual target). A disguised extension is a classic malware delivery
trick, so once uploads exist:

- A mismatch found in an **uploaded** file needs to be treated as a
  real possible attack, not filed alongside decades-old bit rot.
- Real malware scanning (e.g. ClamAV, or a cloud AV API) belongs in the
  upload path itself, before a file is ever accepted onto disk - this
  repo's existing content-sniffing is necessary but not sufficient (see
  README.md's "What this is not").
- Consider quarantining (moving out of the served tree, not just
  excluding from the listing - see below) any upload that fails either
  the sniff check or a malware scan, rather than silently dropping or
  accepting it.
- Rate-limit and/or alert on repeated mismatches from the same
  user/session - a pattern of disguised files is a stronger signal than
  one isolated case.

Not started - flagged by Joakim 2026-07-16, before any upload feature
exists.

## Let each user review their own "cannot be seen" files

Future requirement: rather than mismatches only being visible in the
aggregate `/api/file-summary` list, each user should be able to see
*their own* hidden/excluded files specifically - what was hidden, why
(mismatch details), and safely inspect it (e.g. forced-download with no
execution risk, not opened/rendered in-app). Needed once this is
multi-user - today's single-shared-summary view is fine for one
household, not for isolated per-user libraries.

Not started - flagged by Joakim 2026-07-16.

## Quarantine, not just exclusion

Currently a mismatched file stays exactly where it is in
`mammas_bilder`, just excluded from `/api/tree`'s browsable listing.
That's fine for today's read-only, trusted, single-source library, but
won't be sufficient once uploads exist - actually isolating flagged
files (moving them to a separate quarantine location, not merely hiding
them from one listing endpoint) reduces the chance of a mismatched file
being reached through some other, less-careful code path later.

## Broader magic-number coverage

`.mkv`/`.webm` are accepted by extension in `VIDEO_EXTS` but have no
signature check in `_sniff_file_type`/`_EXPECTED_LABEL_FOR_EXT` yet
(EBML-based container, different magic bytes than the RIFF/`ftyp`
formats currently covered) - low priority while the actual photo
library has none of these, but worth closing before this generalizes
beyond `mamma-photo-viewer`.
