# Similar-faces search returns increasingly wrong matches past the first result

Status: **partially fixed, 2026-09-11** - a real, confirmed self-match bug is fixed (see below). Whether
the landmark-alignment theory explains any *remaining* wrongness is still open, pending Joakim
re-testing the fixed build. Keep this file as the full chronological trail as more is learned - don't
overwrite conclusions.

## Symptom

Joakim, tapping a detected face in the fullscreen viewer (opens `SimilarFacesActivity`, ranked by
`FaceSimilarity.findSimilar`'s cosine similarity over `MobileFaceNetEmbedder`'s 512-d embeddings):
"there are first my face but the following faces are very much not mine" - the top result(s) look
right, ranking degrades quickly after that, well before running out of genuinely similar faces in
the test set.

## Investigation log

1. 2026-09-09: reported by Joakim at the end of the session that built this feature. Not yet
   investigated with real data - no logging of actual similarity scores was captured, no
   comparison against a hand-picked "these two crops are obviously the same person" pair was run.
   Flagging the leading theory below only because it's a *pre-existing, already-documented*
   simplification in the same code path, not because it was actually confirmed this session - see
   `documentation/policies/WORKFLOW.md`'s debugging-discipline rule against fixing from theory
   alone.
2. 2026-09-11: got real data per step 1 below (added a temporary Logcat line to `SimilarFacesActivity.showMatches`,
   kept permanently since it's cheap and clearly useful for exactly this kind of debugging; a second,
   throwaway diagnostic line in `BoundingBoxOverlayView.onDraw` used only to compute exact on-screen
   tap coordinates via `adb shell input tap`/`uiautomator dump` was added and reverted). Drove the real
   emulator end to end (no screenshots, per `WORKFLOW.md`'s GUI-debugging rule): launched the app, let
   the automatic scan finish (109 faces/107 photos, matching the 2026-09-09 handoff), opened photo
   `.../0097_IMG_20250406_140810967.jpg` (a real photo of Joakim) fullscreen, enabled "Show detected
   faces," and tapped the one detected face box.
   - **Root cause #1, CONFIRMED and FIXED**: the real tap's rank-0 result was `similarity=0.99999994`
     - not a real match, the tapped face matching *itself*. `SimilarFacesActivity`'s `findMatches`
     never passed `excludeSelf` to `FaceSimilarity.findSimilar` at all. Worse, even passing it
     wouldn't have worked as written: `SimilarFacesActivity` only ever has a `ScannedFace`
     *reconstructed* from `Intent` extras (the embedding + box), never the same object instance
     `FaceScanCache` holds, and the old exclusion check compared by reference (`!==`). Fixed both
     halves: `FaceSimilarity.findSimilar` now excludes by value (`!=`, using `ScannedFace`'s existing
     structural `equals`/`hashCode`), and `SimilarFacesActivity.createIntent` now carries the full
     tapped `ScannedFace` (embedding + box, not just the embedding) so the reconstructed instance is
     value-equal to the cached one. Verified fixed both in Robolectric (`FaceSimilarityTest`,
     `SimilarFacesActivityTest`, `FullscreenPhotoActivityTest`, plus a new `FaceScanCache.clear()`
     needed to isolate the new test from cross-test-class cache pollution that was otherwise throwing
     `ArrayIndexOutOfBoundsException` inside `cosineSimilarity` on leftover differently-sized
     embeddings from unrelated tests - 82/82 tests green, up from 78) and by re-running the exact same
     real tap on-device: rank 0 is now `similarity=0.690948`, the same real match that was previously
     sitting at rank 1. This plausibly explains at least part of "there are first my face" - that
     "first" result was never a similarity match to begin with, just an identity artifact.
   - **Beyond the self-match bug**: pulled the real on-device JPEGs (via `adb shell content query`
     for each match's `_data` path, then `adb pull`) for 11 of the ranked matches from that same real
     tap - rank 1 (0.69) through rank 59 (0.19, the lowest of the top-60 `topK`) - and visually
     compared each against the tapped photo. Ranks 1 through ~20 (similarity ~0.69 down to ~0.33)
     were **all** the same person as the tapped face, across genuinely different poses/lighting/crops
     (mirror selfies, a train selfie, a castle photo with a second person, a dinner photo with a third
     person). Rank 59 (0.19, a photo of a clearly different, unrelated person) was correctly *not* a
     match. One sample around rank 26 (0.30, a busy multi-person church christening photo) was
     inconclusive - no face in that photo obviously resembled the tapped person, plausibly a real
     false positive, but it's a crowded multi-face scene so not conclusive either way.
   - **Net read**: for this specific real tap, ranking quality past the (now-fixed) bogus rank-0 was
     substantially better than the original "very much not mine" complaint suggested - confirmed
     matches persisted well past "the first result," only degrading around similarity ~0.3 and below,
     consistent with step 3's "not enough real matches in this photo set" explanation rather than a
     fundamental embedding/crop-alignment defect. Full rank/similarity/URI list from this run kept in
     this session's own history for reproducibility if needed; not pasted here to keep this file lean.
   - **Not yet resolved**: whether Joakim's original complaint had a different cause (a different,
     lower-quality face tapped originally; a worse crop; or simply misreading the old bogus rank-0
     "self" result plus the genuinely-correct rank-1 as "the first one, then wrong") is still open -
     the self-match bug alone doesn't cleanly account for "very much not mine" appearing as early as
     described, given how good the confirmed-correct stretch actually was here. **Next step is for
     Joakim to re-test the fixed build and report whether it still looks wrong, and if so, on which
     photo/tap** - only then does step 4 (landmark-based crop alignment) become worth scoping.
3. 2026-09-11, same session, shortly after: Joakim independently (unprompted, relayed via a peer
   session, `differentiate-pictures-for-auto-sync-b1`) reported: "when clicking a picture, the
   suggested pictures are good, at the begining but later on gets mixed up with other faces, not the
   original one." This **matches, not contradicts**, the 2026-09-11 real-data finding above - "good
   at the beginning" lines up with the confirmed-correct rank-1-through-~20 stretch (similarity ~0.69
   down to ~0.33), "mixed up later" lines up with the observed degradation below ~similarity 0.3. So
   this is real, independent confirmation that *something* genuinely degrades past a similarity
   threshold - not just an artifact of the (now-fixed) self-match bug, and not fully resolved by that
   fix alone. Still doesn't distinguish between step 2's embedding-quality theory and step 3's
   "not enough real matches in this photo set" theory - both predict this exact pattern. Peer session
   has asked Joakim for the specific photo/tap to get a second reproducible real-data sample.

## Leading theory (unconfirmed)

`FaceRecognitionPipeline.cropFace` (and `SimilarFacesAdapter.cropMatchedFace`, which crops the same
way for display) both do a plain axis-aligned crop of the detected box plus a fixed margin - not
the landmark-based similarity-transform alignment (warping to ArcFace's canonical 5-point pose)
that MobileFaceNet-family models are trained on and are known to be sensitive to. An off-center or
tilted face crop plausibly degrades embedding quality enough to explain "close match first, then
noise" - but this has NOT been confirmed against real embedding/score data. Other equally-plausible
unconfirmed causes: the embedding preprocessing (RGB order / (pixel-127.5)/127.5 normalization,
`MobileFaceNetEmbedder.kt`) could have a subtle error despite being checked against InsightFace's
own `inference.py` this session; or the model itself may just be weaker than expected at this
crop/margin ratio; or there may be too few faces of the same person in the test photo set for the
"later" ranks to have any real match available at all, making "wrong" the expected, correct
behavior for those positions specifically.

## Next session should start with (2026-09-11 update)

Steps 1-3 below are done, see the 2026-09-11 investigation-log entry above for the real data and
conclusion. What's actually next:

1. Ask Joakim to re-test similar-faces search on the fixed build (self-match bug gone) and report
   whether results still look wrong, and on which photo/tap if so - the 2026-09-11 sample tap showed
   substantially correct ranking down to similarity ~0.3, so don't assume the original complaint is
   fully explained without a fresh report against the fixed build.
2. Only if a fresh, reproducible bad case turns up, consider landmark-based crop alignment (still a
   real chunk of new work) - the original 2026-09-09 "leading theory" below is still unconfirmed
   either way, not ruled out by the 2026-09-11 data, just not the best next step until there's a
   concrete bad case to test it against.

## Next session should start with (2026-09-09, historical - see the update above)

1. Get real data before touching any code: log the actual `FaceMatch.similarity` scores for one
   real tap (Logcat is fine), and separately compute cosine similarity by hand between two crops
   Joakim confirms are obviously the same person, to see what a "real match" score even looks like
   in this pipeline - right now there's no baseline to compare against.
2. If scores for wrong matches are *not* meaningfully lower than the right ones, the embedding
   itself is likely the problem (preprocessing bug or model/crop-quality issue) - check that before
   touching the ranking code, which is simple and already unit-tested (`FaceSimilarityTest`).
3. If scores for wrong matches *are* meaningfully lower, this may just be "not enough real matches
   exist in this photo set" rather than a bug - confirm with Joakim what he actually expected to
   see before assuming something's broken.
4. Only then consider whether to build proper landmark-based crop alignment (a real chunk of new
   work, not a quick fix) - don't jump to implementing it on the unconfirmed theory above.
