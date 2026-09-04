# Build modules/pictures.py, session 3 of the pictures pipeline

Session 3 of the pictures pipeline: `GetListOfValidPictureFiles()`, a central SQLite
`pictures`/`locations` register (one picture keyed by MD5, many recorded locations,
incremental rescans, `statx(2)`-via-`ctypes` birth time with a documented fallback), so photos
from disparate sources (local folders, sshfs NAS mounts) land in one place over time. Also:
confirmed and closed the `test_main.py` X BadAlloc bug; logged two new bugs from live
`test_main.py` testing feedback (blur-metric miscalibration, low-confidence-band false
positives, with a `person`-class recall-over-precision requirement captured); and designed the
privacy guardrails a future contacts-import face-labeling feature would need.

- **Doc size**: GLOSSARY.md +1840, PICTURES_PIPELINE.md +2525, data-modeling/TODO.md +312,
  THREATS.md +2989, tags/TODO.md +241, modules/README.md +1177, the X-BadAlloc bug report
  (moved to fixed/) +192, two new bug reports +4507 and +2945.
