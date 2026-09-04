# Build modules/objects.py, NanoDet-Plus object detector

Session 2 of the restart's pictures pipeline: `modules/objects.py` (NanoDet-Plus, Apache-2.0,
COCO's 80 classes), TDD'd against a mocked ONNX forward pass and confirmed against real photos.
`modules/quality.py` retrofitted with `check_all()` so every `modules/` detector now exposes a
combined-result object alongside its bare per-check functions. `modules/test_main.py` added as a
manual, local-only tkinter dev tool (folder picker -> findings window), not a pytest test.

- **Doc size**: GLOSSARY.md +2012, PICTURES_PIPELINE.md +2849, data-modeling/TODO.md +3,
  modules/README.md +685 (Unicode codepoints, +5549 total).
