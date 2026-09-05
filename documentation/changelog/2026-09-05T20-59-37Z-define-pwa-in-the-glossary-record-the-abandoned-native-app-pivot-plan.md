# Define PWA in the glossary, record the abandoned native-app-pivot plan

Mid-session the scope pivoted from "make the pictures web viewer usable from a phone" toward a
native Android app (photos must be handled/differentiated on-device before any server copy, with
selective sync triggered automatically in the background - no browser API reaches that). Joakim
abandoned this session for a fresh one given the scope change, but two artifacts from the discovery
are worth keeping: a GLOSSARY.md definition for PWA (used throughout existing docs, never actually
defined), and documentation/plans/shimmering-wondering-swing.md - a plan (never formally approved,
`ExitPlanMode` errored before review) capturing real research the next session shouldn't have to
redo: master lacks modules/pictures.py entirely (only test_production1 has it), the old Postgres/
FastAPI stack under archive/ is confirmed disregarded per its own README, this machine has no JDK/
Android SDK but does have Docker, and the reasoning for reversing the repo's "avoid native app"
stance (sideloaded APK preserves the original app-store-control concern). Kept as historical record
per this repo's existing documentation/plans/ convention (other plan files there aren't removed
after being acted on or abandoned either).

- **Doc size** (Unicode codepoints): `documentation/GLOSSARY.md` 58,076 → 59,105 (+1,029); `documentation/plans/shimmering-wondering-swing.md` new file, 7,366.
