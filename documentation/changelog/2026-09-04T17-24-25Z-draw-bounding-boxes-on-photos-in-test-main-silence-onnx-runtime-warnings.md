# Draw bounding boxes on photos in test_main, silence ONNX Runtime warnings

`modules/test_main.py`'s results window now draws each detection's box + label directly on the
photo (PIL ImageDraw) in a scrollable canvas, instead of a separate text-only pane - lets Joakim
scroll through a whole folder and see what NanoDet-Plus found at a glance. Also set
`SessionOptions.log_severity_level=3` on the ONNX session (`modules/objects.py`) to silence
~150 lines of harmless-but-noisy "Initializer appears in graph inputs" warnings this model's
export triggers on every load, spotted when Joakim ran the tool for the first time.

- **Doc size**: modules/README.md +76.
