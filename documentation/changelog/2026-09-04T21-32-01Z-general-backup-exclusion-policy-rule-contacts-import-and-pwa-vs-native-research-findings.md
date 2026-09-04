# General backup-exclusion policy rule, contacts-import and PWA-vs-native research findings

Joakim asked for the backup-exclusion guardrail generalized beyond Android specifically, plus real
research (not assumption) on whether the contacts-import/photo-picking features actually need a
native app. Web-searched: Contact Picker API has zero desktop browser support (mobile-only);
Chrome Sync doesn't include IndexedDB, so a PWA's local storage structurally avoids the
backup-to-cloud leak Android's native-app auto-backup creates; File System Access API covers
one-time photo picking fine from a PWA; iOS Safari has no Background Sync support, the one real
gap forcing native for *automatic* background behavior specifically.

- **Doc size**: POLICY.md +1345, THREATS.md +744, curation/ARCHITECTURE.md +1204, GLOSSARY.md
  +1658.
