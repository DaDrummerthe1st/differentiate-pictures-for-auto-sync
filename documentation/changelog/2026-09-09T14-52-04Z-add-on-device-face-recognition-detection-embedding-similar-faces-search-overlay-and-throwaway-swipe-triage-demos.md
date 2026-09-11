# Add on-device face recognition (detection, embedding, similar-faces search, overlay) and throwaway swipe-triage demos

On-device face detection (YuNet) + embedding (MobileFaceNet, 512-d) via ONNX Runtime Mobile,
running automatically over the visible gallery on launch; an off-by-default bounding-box overlay
in the fullscreen viewer only; tap-a-face similar-faces search via cosine similarity
(`SimilarFacesActivity`/`FaceSimilarity`). ONNX Runtime Mobile was a pragmatic unblocking choice
(MNN's Maven AAR has no usable native libs on this x86_64 emulator), not a resolution of the
still-open OpenCV-vs-MNN-vs-ONNX runtime conflict across branches — Joakim's call: defer
standardizing, revisit in a dedicated session (see mobile/TODO.md). Also two throwaway
swipe-triage grid demos (multi-select + swipe, fake Toast/log persistence only) per the design
spec in UX_FLOWS.md. Filed a new under-investigation bug for degrading similar-faces match
quality past the first result, and corrected DETECTORS.md's stale 128-d MobileFaceNet figure to
the real vendored model's 512-d output.

- **Doc size**: `documentation/curation/DETECTORS.md` +373 chars; `documentation/mobile/README.md`
  +454 chars; `documentation/mobile/TODO.md` +3,394 chars (delta against HEAD at commit time,
  after a concurrent peer session's own TODO.md edit already landed separately); new bug file
  `documentation/bugs/repo/under_process/2026-09-09-similar-faces-search-returns-increasingly-wrong-matches-past-the-first-result.md`
  +3,494 chars.
