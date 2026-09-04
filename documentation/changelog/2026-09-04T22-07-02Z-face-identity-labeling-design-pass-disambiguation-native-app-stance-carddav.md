# Face-identity-labeling design pass: disambiguation, native-app stance, CardDAV

Asked Joakim rather than assume, per WORKFLOW.md's "ask or search" rule: (1) what a labeled person
needs beyond a name to solve "two Per Holmgrens" — resolved as required-at-creation, not
collision-triggered: every person entity's `attributes` now needs a `disambiguation_note` and
`reference_photo_id` from the start; (2) whether automatic background DFS redundancy-contribution
is wanted badly enough to justify a native app — resolved no, and Joakim's reasoning (app stores can
modify/re-sign a published binary, conflicting with self-hosted-NAS control) generalizes into a
standing "avoid native app as long as possible" architectural stance, not just this feature's answer;
(3) the desktop contacts-fallback, since Contact Picker API has no desktop support — Joakim asked
whether something like Thunderbird's contact syncing exists. Web-searched and confirmed CardDAV
(RFC 6352) is real and widely supported (Google, iCloud, Thunderbird); chosen as the target design,
with re-sync-on-not-found required rather than a frozen export, but it reopens THREATS.md row 17's
bulk-list-exposure tradeoff on desktop specifically (not yet resolved). Real build (needs Joakim's own
Google OAuth client / iCloud app-specific password) deferred to a separate guided session, not
attempted here.

- **Doc size**: GLOSSARY.md +925, curation/ARCHITECTURE.md +361, curation/IDENTITY_MATCHING.md
  +6607, security/THREATS.md +1220, tags/SCHEMA.md +174, tags/TODO.md +824.
