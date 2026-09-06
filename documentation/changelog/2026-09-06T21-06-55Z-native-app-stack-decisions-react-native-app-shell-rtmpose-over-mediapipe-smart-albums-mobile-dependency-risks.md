# Native app stack decisions: React Native app shell, RTMPose over MediaPipe, Smart Albums, mobile dependency risks

Parsed the native-app-pivot's remaining open threads with Joakim: picked React Native as the app
shell (Linux Foundation governance, native modules for OpenCV/WireGuard), promoted RTMPose over
MediaPipe for pose (re-verified its license concern was actually answered by a maintainer), designed
Smart Albums as a saved query (not a new tag category), added a visible-payoff requirement to the
gamification credit mechanic, and flagged two real risks found via research (PhotoView archived,
Intel's Open Model Zoo deprecated, sqlite-vec blocked by Apple on iOS) rather than leaving stale picks
in place.

- **Doc size** (Unicode codepoints): `documentation/GLOSSARY.md` 63,258 → 74,768 (+11,510); `documentation/curation/DETECTORS.md` 44,541 → 47,014 (+2,473); `documentation/tags/TAXONOMY.md` 15,051 → 18,104 (+3,053); `documentation/curation/GAMIFICATION.md` 12,398 → 14,036 (+1,638); `documentation/distributed-sync/METADATA.md` 5,763 → 6,910 (+1,147); `documentation/VISION.md` 18,001 → 18,767 (+766).
