# Pick OpenCV-first mobile inference runtime, DBSCAN face clustering, sync privacy-messaging note

Discussion session on the native-app pivot's actual on-device AI stack (Kotlin now, Swift later).
`curation/DETECTORS.md` gets a new cross-cutting "Mobile runtime" section: OpenCV (Apache-2.0, one
codebase across Android/iOS/Linux) as the default engine, verified via web search rather than
assumed — real ONNX-importer operator-coverage gaps and weaker Android GPU/NNAPI support found,
so ONNX Runtime Mobile (MIT) stays a narrow fallback for NanoDet-Plus/MobileFaceNet specifically,
pending a concrete compatibility check (TODO, not yet done). Also records face clustering (DBSCAN
over MobileFaceNet embeddings, no new model) as distinct from the already-picked face-recognition
mechanism. `tags/UX_FLOWS.md` gets a parked note: the sync/backup setup screen must plainly tell
the user that no other copy of her data exists by default, and that a free FOSS server app is the
first-class self-hosting option. `GLOSSARY.md` gains the terms explained in chat this session
(confidence score, face clustering, DBSCAN, NNAPI/execution provider, ML Kit, AAR, MobileFaceNet,
in-process library, local-first, cluster centroid).

- **Doc size** (Unicode codepoints): `documentation/GLOSSARY.md` 59,099 → 63,258 (+4,159); `documentation/curation/DETECTORS.md` 40,766 → 44,541 (+3,775); `documentation/tags/UX_FLOWS.md` 8,468 → 9,484 (+1,016).
