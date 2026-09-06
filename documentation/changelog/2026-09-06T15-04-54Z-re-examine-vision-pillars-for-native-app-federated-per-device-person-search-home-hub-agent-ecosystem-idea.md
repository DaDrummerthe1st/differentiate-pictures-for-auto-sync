# Re-examine VISION pillars for native app, federated per-device person search, home-hub agent-ecosystem idea

Continuing the native-app-pivot discussion: re-examined VISION.md's four pillars one at a time
with Joakim. Pillar 1 gets an explicit phone-as-first-compute-node note (the app's sync-to-your-
own-server feature is the on-ramp into the DFS pillar, not a separate mechanism) plus a captured
future idea — the home NAS eventually hosting general LLM/agent capabilities over open formats
(CalDAV/CardDAV-style), opening a third-party developer ecosystem (Joakim's example: smart
mirrors). Pillar 2 gets a real architecture answer to "how does person-search work across phone +
NAS + DFS, for stills and video clips both": a federated *per-device query*, not a federated index,
extending distributed-sync/METADATA.md's already-resolved 2026-07-29 private-face-matching design
from one device to several — `sqlite-vec` (MIT/Apache-2.0, verified via web search) as the mobile
equivalent of the NAS's pgvector, the phone acting as a "remote control" merging its own local
results with a query forwarded to the NAS. Also recorded: finding people (photos and clips) is a
stated core USP, not a secondary filter.

- **Doc size** (Unicode codepoints): `documentation/VISION.md` 14,993 → 16,575 (+1,582); `documentation/distributed-sync/METADATA.md` 4,372 → 5,763 (+1,391); `documentation/distributed-sync/README.md` 4,966 → 5,667 (+701).
