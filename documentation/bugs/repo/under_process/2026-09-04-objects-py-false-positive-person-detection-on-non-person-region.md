# objects.py false-positive person detection on non-person region

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim, running `modules/test_main.py` against a real conference-room photo
(`0010_IMG_20240304_165107_243.jpg`): NanoDet-Plus reports a **"person" at 44% confidence**,
`bbox=(3690, 1680, 3810, 1880)`, on the far right of the frame — a small, blurry patch of what
appears to be a white door/cabinet panel, not a person. His words: "The absolute right is not a
person. Very blurry picture upon that [region]."

## Investigation log

1. `modules/objects.py`'s `SCORE_THRESHOLD` default is `0.4` (`OBJECTS_SCORE_THRESHOLD` env
   var) — 44% clears that bar today, so this isn't a thresholding accident, it's a genuine
   false-positive detection at a confidence the current default treats as real.
2. The flagged region is small in the frame and, per Joakim, itself blurry/low-detail — plausibly
   under-informative input for the detector at that crop size, consistent with NanoDet-Plus (or
   any COCO-trained detector) being less reliable on small, low-contrast, ambiguous regions than
   on large, clear ones. Not yet independently verified by inspecting the actual crop pixels.
3. Not yet checked: whether this is a one-off (this specific photo) or a systematic pattern —
   needs testing against more real photos before concluding whether `SCORE_THRESHOLD=0.4` is
   too permissive in general, or whether this is an isolated hard case.
4. Second false positive found same session, different class: a photo of a pen (with a
   "margretetorp.se" branded barrel) reported "knife 42%" — again just above the 0.4 threshold.
   This is now two independent false positives in the low-40s% band, on two different classes
   (`person`, `knife`), suggesting the confidence-band unreliability may not be person-specific —
   widens the scope of the "Next session should start with" evidence-gathering pass below beyond
   just the `person` class, though the person-specific recall-over-precision requirement above
   still stands as the sharpest priority.
5. Related but distinct, same session: a kitchen photo with two real cats got two overlapping
   detections at the same location — `cat 48%` and `dog 54%` — i.e. one of the two cats was
   misclassified as `dog`. Joakim's read was net-positive ("I like the fact it detected two"),
   not a complaint — logged here as more same-confidence-band evidence (cross-species confusion
   between visually similar COCO classes), not as its own bug.

## Design requirement, confirmed by Joakim 2026-09-04

For the person class specifically, **recall matters far more than precision**: missing a real
person (a false negative) is the problem worth avoiding; flagging a non-person as "person" at
low confidence (a false positive, like this bug) is a much smaller cost — a wrong guess is easy
to discard downstream, a missed person is a photo that silently never gets the "has a person in
it" treatment at all. This points toward **not** raising `SCORE_THRESHOLD` as a response to this
bug, and if anything reconsidering whether it's currently too high (i.e. erring toward a lower
threshold for `person` specifically, accepting more false positives like this one in exchange for
fewer missed people) rather than tightening it. Not yet acted on — still needs the same
confidence-band evidence gathering below before changing the default, now with this priority
explicitly guiding which direction a change should go.

## Leading theory (unconfirmed)

A single false positive at 44% confidence on a small, blurry, ambiguous region — could be
addressed by raising `SCORE_THRESHOLD` (fewer false positives, but also fewer true positives on
genuinely small/distant people), or could just be normal, expected model error at this
confidence level that downstream consumers (e.g. session 3's prioritization step) should treat
as "worth a second look," not "certainly a person." Not yet decided which.

## Next session should start with

Run `modules/objects.py` (or `test_main.py`) against a wider sample of real photos and log
confidence vs. correctness for detections in the 40-60% band specifically, to see whether this
is a systematic low-confidence accuracy problem (in which case a higher default
`SCORE_THRESHOLD`, or surfacing confidence to downstream consumers rather than a bare
yes/no, is the fix) or an isolated case not worth changing the default over.
