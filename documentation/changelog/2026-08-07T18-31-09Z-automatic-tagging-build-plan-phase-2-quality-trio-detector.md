# Automatic-tagging build plan Phase 2: quality trio detector

Phase 2 of curation/TODO.md's automatic-tagging build plan (Phase 0-1 done in the previous session):
`detector/quality.py` adds `detect_blur` (variance of Laplacian), `detect_exposure` (mean luminance,
over/under/normal), and `detect_monochrome` (mean HSV saturation) — no model, pure functions over a
`PIL.Image`, thresholds as named env-overridable constants. Wired behind a new `POST /detect` on the
`detector` service, returning tags in the same `{category, value, bbox_x/y/w/h}` shape
`app/main.py`'s `TagCreate` already uses, so Phase 5's orchestration job can insert the response
directly. TDD against synthetic PIL checkerboard fixtures (solid colors are degenerate for the blur
metric — always reads maximally blurry — so fixtures keep edge content to isolate each signal; that
behavior is itself asserted by a named test, not hidden). Full suite green
(`detector/tests/test_quality.py`, `detector/tests/test_detect.py`, 110 tests total across
`detector/`+`app/`), plus a real end-to-end smoke test against the built container image (a synthetic
JPEG POSTed to `/detect` from inside the running container matched unit-test predictions exactly),
then torn down. Docs updated same pass: DETECTORS.md's quality-trio rows flipped to "built", a new
GLOSSARY.md entry for "variance of Laplacian", and curation/TODO.md's build-plan section moved to
"Phase 0-2 done, Phase 3 next" plus a new note recording Joakim's mid-session ask (workstation load
visibility once real models load in Phase 3/4, and a `.10` deploy with monitoring/logging once Phase
6 passes) — neither designed yet, flagged for a decision before Phase 6/7.

- **Doc size**: `documentation/GLOSSARY.md` +403 chars.
- **Doc size**: `documentation/curation/DETECTORS.md` +115 chars.
- **Doc size**: `documentation/curation/TODO.md` +2361 chars.
