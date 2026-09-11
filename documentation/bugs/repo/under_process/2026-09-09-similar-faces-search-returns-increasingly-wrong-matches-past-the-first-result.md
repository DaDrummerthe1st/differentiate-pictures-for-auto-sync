# Similar-faces search returns increasingly wrong matches past the first result

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

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

## Next session should start with

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
