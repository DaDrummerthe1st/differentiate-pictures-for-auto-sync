# Vendored model licenses

Fetch-once, commit-once convention (same as `archive/detector/models/LICENSES.md`'s, carried
forward for `modules/` independently) - models are downloaded from their upstream release,
committed here, and never fetched at build or run time.

## nanodet-plus-m_416.onnx

- **Source**: https://github.com/RangiLyu/nanodet/releases/download/v1.0.0-alpha-1/nanodet-plus-m_416.onnx
- **License**: Apache-2.0 (Copyright 2020-2021 RangiLyu) - the repo's own root `LICENSE` file,
  checked directly. Unlike YuNet's case (`archive/detector/models/LICENSES.md`), this ONNX file
  is exported from this same repo's own training code/weights, not a third-party vendored asset
  with its own separate license file - no separate per-model license exists to diverge from the
  repo root here.
- **SHA-256**: `59d2f166088889c902f523bf08079391993491324f0d84847e3c4016a8f7cc3d`
- **Used by**: `modules/objects.py` via `onnxruntime.InferenceSession`.
- **Preprocessing note**: this plain ONNX export does *not* bake in input normalization (unlike
  the repo's OpenVINO IR demo, whose `.xml` has it folded in via model-optimizer flags) - the
  mean/std used at training time (`config/nanodet-plus-m_416.yml` upstream:
  `[[103.53, 116.28, 123.675], [57.375, 57.12, 58.395]]`, BGR order) must be applied by the
  caller. Confirmed empirically: raw un-normalized input produced nonsensical high-confidence
  detections (e.g. "parking meter" at 100%) on a real test photo; applying this normalization
  fixed it.
