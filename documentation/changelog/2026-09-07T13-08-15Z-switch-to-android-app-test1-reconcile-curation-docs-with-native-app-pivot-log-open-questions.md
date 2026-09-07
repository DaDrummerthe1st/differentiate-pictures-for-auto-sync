# Switch to android-app-test1, reconcile curation docs with native-app pivot, log open questions

Sideloaded the Kotlin app and switched back to it (`android-app-test2`, already fully merged into
`master`, deleted both locally and on origin — nothing lost). Scoping a new round of app features
(on-device storage, object/scene detection, contacts linking, gamified confidence display) surfaced
that `curation/` already has deep design for most of this from the pre-native-app-pivot era; updated
its scope note to flag the on-device porting gap instead of re-designing, and logged the on-device
storage decision (Room, log-then-recompute) and a genuinely new open question (tied/ambiguous
scoring) that isn't addressed anywhere yet. Added a `GLOSSARY.md` entry for "confidence score."

- **Doc size**: `curation/README.md` +545 chars, `GLOSSARY.md` +905 chars, `mobile/TODO.md` +2469
  chars, `curation/TODO.md` +1034 chars.
