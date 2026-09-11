# Vendored model licenses

Fetch-once, commit-once convention (same as
`previous-work/multi-user-web-app/detector/models/LICENSES.md`) — models are downloaded from their
upstream release, committed here, and never fetched at build or run time. Model picks themselves
are researched in [documentation/curation/DETECTORS.md](../../../../../../documentation/curation/DETECTORS.md)
area B; this file only tracks the actual vendored artifacts.

## face_detection_yunet_2023mar.onnx

- **Source**: https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
- **License**: MIT (Shiqi Yu) — same file already vendored server-side, same license finding, see
  `previous-work/multi-user-web-app/detector/models/LICENSES.md`.
- **SHA-256**: `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`
- **Used by**: `facerecognition/YuNetFaceDetector.kt` via ONNX Runtime Mobile (raw ONNX graph, not
  OpenCV's `FaceDetectorYN` convenience API — decode/NMS reimplemented in Kotlin from
  `opencv/opencv`'s `modules/objdetect/src/face_detect.cpp`, the ground-truth source for this exact
  model's `cls_*`/`obj_*`/`bbox_*`/`kps_*` output layout).

## arcface_mobilefacenet.onnx

- **Source**: https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/FaceRecognition/arcface/arcface_mobilefacenet/pretrained/2022-08-24/arcface_mobilefacenet.zip
  (`mbf.onnx` inside the zip, renamed on vendoring for clarity) — referenced from
  `hailo-ai/hailo_model_zoo`'s `cfg/networks/arcface_mobilefacenet.yaml`.
- **License**: MIT — `hailo-ai/hailo_model_zoo`'s own repo-wide MIT license and model card
  (`license_url: https://opensource.org/licenses/MIT`), re-verified 2026-08-05 in
  `documentation/curation/DETECTORS.md` area B and `research-findings` repo's
  `2026-08-05-license-reverification-and-privacy-reads.md` (one flagged, non-reversing nuance:
  training data shares InsightFace-format lineage, but Hailo's own redistribution terms carry no
  separate restriction, unlike InsightFace's own non-commercial-research clause on `buffalo_*`).
- **SHA-256**: `1ef27ee20b9264f00f65d59b2be340001a012ffd686fe6b835ec0d702820f5c9`
- **Real output shape correction (found 2026-09-09, on-device build)**: this model outputs a
  **512-d** embedding (`[1, 512]`), not the 128-d figure `DETECTORS.md`/`GLOSSARY.md` currently
  state — that number described MobileFaceNet variants generally, not specifically checked against
  this exact vendored file until now. Doesn't affect the pick, just the embedding dimension to code
  against.
- **Preprocessing (verified against `deepinsight/insightface`'s own `recognition/arcface_torch/inference.py`,
  not assumed)**: 112x112 input, **RGB** channel order (source does `cv2.imread` (BGR) then
  `cv2.cvtColor(..., COLOR_BGR2RGB)` before feeding the network), normalized as
  `(pixel - 127.5) / 127.5` (range [-1, 1] per channel) — matches
  `hailo_model_zoo`'s own `mean_list`/`std_list` of `[127.5, 127.5, 127.5]` each.
- **Used by**: `facerecognition/MobileFaceNetEmbedder.kt` via ONNX Runtime Mobile.
