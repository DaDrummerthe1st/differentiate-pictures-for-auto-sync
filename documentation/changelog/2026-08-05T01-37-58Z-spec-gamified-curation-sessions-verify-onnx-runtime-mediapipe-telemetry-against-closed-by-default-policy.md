# Spec gamified curation sessions; verify ONNX Runtime/MediaPipe telemetry against closed-by-default policy

New [documentation/curation/GAMIFICATION.md](../curation/GAMIFICATION.md), generalizing
UX_FLOWS.md's narrow identity-only gamification sketch into every confirm/correct/decline round type,
deciding the credit mechanic UX_FLOWS.md had left open (tied to training value contributed, not
correctness; no dark patterns), excluding privacy-category decisions from gamification entirely, and
resolving the "system-wide training" question against the project's existing no-shared-embeddings
stance while flagging a narrower opt-in anonymized-correction-export path as the buildable
interpretation. Separately, checked whether today's four new model picks are appropriate for this
project's closed-by-default posture: found ONNX Runtime (underlying most of DETECTORS.md's picks)
ships telemetry on by default on Windows builds (not Linux, this project's actual target) — logged as
an action item, not a live risk. MediaPipe's on-device-only inference was confirmed by multiple
sources; a separate framework-level telemetry channel was not independently confirmed either way,
flagged as unverified rather than assumed clean.

- **Doc size**: `documentation/curation/GAMIFICATION.md` — +12398 chars (new file); `documentation/curation/TODO.md` — +1263 chars; `documentation/tags/UX_FLOWS.md` — +508 chars; `documentation/GLOSSARY.md` — +862 chars; `documentation/curation/README.md` — +315 chars (all Unicode codepoints, per DOC_METRICS.md methodology).
