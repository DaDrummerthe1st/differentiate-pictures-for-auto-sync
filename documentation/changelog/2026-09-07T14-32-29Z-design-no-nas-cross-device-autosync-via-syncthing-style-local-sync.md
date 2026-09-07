# Design no-NAS cross-device autosync via Syncthing-style local sync

Joakim asked what happens if a user runs the app on an iPad and Android phone but refuses to buy a
NAS or cloud tier. Confirmed this must be a first-class case, not degraded, per POLICY.md's
closed-by-default stance and the native-app pivot's on-device-first premise. Answer: direct
device-to-device autosync over a local network, reusing Syncthing (already vetted prior art in
distributed-sync/NETWORK_MECHANISM.md for a different purpose) rather than designing a new
protocol — QR-code device pairing once, automatic after. Flagged two real, undecided items: this
only works when devices share a network at the same time (a NAS stays the only always-on option),
and Joakim wants per-picture/folder/tag sync granularity, which doesn't map onto Syncthing's native
per-folder sync unit — left as an open architecture fork for the NAS/sync session.

- **Doc size**: `curation/IDENTITY_MATCHING.md` +2143 chars, `GLOSSARY.md` +975 chars.
