# Research four more curation areas: group/co-presence, age/gender, OCR-in-frame, human action/pose

Per Joakim's explicit go-ahead to research everything that comfortably fits in one session rather
than DETECTORS.md's usual one-area-per-session cadence, ran three model-pick surveys as parallel
background agents (kept the calling session's own context lean) and resolved a fourth directly:
group/co-presence needs no new model (a query over the already-picked face-recognition matches);
age/gender picked OpenVINO's `age-gender-recognition-retail-0013` (Apache-2.0); OCR-in-frame picked
RapidOCR (Apache-2.0, avoids a documented ~43GB-RAM bug in stock PaddleOCR); human action/pose (area
J's first research pass ever) picked MediaPipe Pose for keypoints but found no confident pretrained
pick for action classification, resolved to a self-trained keypoint-heuristic approach instead — same
shape of finding as the project's earlier pet-identity survey. Landmark/place recognition and image
captioning remain queued for a future session. Full surveys:
`2026-08-05-ocr-in-frame-engine-survey.md`, `2026-08-05-age-gender-estimation-model-survey.md`,
`2026-08-05-human-action-pose-recognition-survey.md` in the `research-findings` repo.

- **Doc size**: `documentation/curation/DETECTORS.md` — +7599 chars; `documentation/curation/RESEARCH_QUEUE.md` — +1649 chars; `documentation/curation/TODO.md` — +602 chars; `documentation/GLOSSARY.md` — +2850 chars (all Unicode codepoints, per DOC_METRICS.md methodology).
