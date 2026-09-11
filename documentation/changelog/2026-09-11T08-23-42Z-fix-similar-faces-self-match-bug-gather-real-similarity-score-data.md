# Fix similar-faces self-match bug, gather real similarity-score data

`SimilarFacesActivity` never excluded the tapped face from its own results (and couldn't have, as
written — it only ever sees a `ScannedFace` reconstructed from `Intent` extras, never the same
instance `FaceScanCache` holds, while the old exclusion check compared by reference), so every tap's
bogus top "match" was really the tapped face matching itself at ~1.0 similarity. Fixed by excluding
by value instead and passing the full tapped face (not just its embedding) through the Intent; added
`FaceScanCache.clear()` for test isolation. Also drove the real emulator end to end (no screenshots)
to get the first real similarity-score data for the open similar-faces-ranking bug, visually
confirming ranking quality is substantially better than originally reported once the self-match bug's
bogus result is excluded. 82/82 tests green (up from 78).

- **Doc size**: `documentation/bugs/repo/under_process/2026-09-09-similar-faces-search-...md`
  3,494 → 9,342 chars (+5,848); `documentation/mobile/TODO.md` 18,640 → 19,079 chars (+439);
  `documentation/mobile/README.md` 7,134 → 8,478 chars (+1,344).
