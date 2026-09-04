# quality.py blur metric underestimates real motion blur

Status: **investigating, not fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

Joakim, running `modules/test_main.py` against real photos: `0009_IMG_00004_BURST20230915142509.jpg`
(motorola moto e20, 1/17s, ISO 500) is visibly, severely motion-blurred — unreadable text,
smeared edges throughout — but `check_blur` reports only **42.2%** (`quality.py`'s scale calls
>50% "blurry"), i.e. the metric calls this photo *more sharp than blurry*. His words: "This
picture is the definition of blurry, still it is 'only' 42%."

## Investigation log

1. `check_blur` (`modules/quality.py:32`) is variance-of-Laplacian: `blur% = (1 - variance /
   SHARPNESS_VARIANCE) * 100`, clamped to [0, 100], with `SHARPNESS_VARIANCE` defaulting to
   `100.0`. A reported 42.2% back-calculates to a measured Laplacian variance of ~57.8 on this
   photo.
2. `DETECTORS.md` area A already picked variance-of-Laplacian as the technique (researched
   2026-08-02) but the picked default threshold (`100.0`) has not been calibrated against real
   photos from this project's own corpus — it was carried in as a reasonable-sounding default,
   not derived from a labeled sample.
3. Not yet confirmed, but a real candidate explanation: variance-of-Laplacian is well known in
   the literature to respond more weakly to **motion blur** (directional smearing, which can
   still leave real high-frequency edge content perpendicular to the motion axis) than to
   **defocus blur** (uniform, isotropic softening) — this photo is a fast-shutter handheld
   motion-blur case (1/17s), not an out-of-focus case. If true, the technique itself may need a
   second signal for motion blur specifically, not just a threshold change.

## Leading theory (unconfirmed)

Either (a) `SHARPNESS_VARIANCE=100.0` is simply too low a ceiling for this camera/sensor's real
photos and needs recalibration against a labeled sample set, or (b) variance-of-Laplacian
under-detects motion blur specifically (a known technique limitation, not a tunable-threshold
problem) and a second, motion-specific signal is needed alongside it. Not distinguished yet -
needs a real calibration pass, not a guessed new constant.

## Next session should start with

Pull a small labeled sample (a handful of photos Joakim would call "sharp," "mildly blurry,"
and "very blurry," including at least one motion-blur case like this one) from
`resources/test_pictures/`, run `check_blur` against each, and see whether *any* single
`SHARPNESS_VARIANCE` value separates them correctly. If motion-blur cases stay systematically
under-scored even after retuning the threshold, treat that as confirming theory (b) above and
research a motion-blur-specific technique (e.g. directional gradient variance) as a follow-up
signal, rather than continuing to tune the single Laplacian-variance threshold.
