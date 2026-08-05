# Add TFLite glossary entry, prompted by a Coral-accelerator question

Joakim asked what "TFLite-only, not ONNX" actually meant and whether it was glossaried — it wasn't
(ONNX/ONNX Runtime already was). Added a TFLite entry explaining it's a separate, non-interoperating
format/runtime ecosystem from ONNX, and why that's why Coral doesn't drop cleanly into this project's
current picks.

- **Doc size**: `documentation/GLOSSARY.md` — +575 chars (Unicode codepoints, per DOC_METRICS.md methodology).
