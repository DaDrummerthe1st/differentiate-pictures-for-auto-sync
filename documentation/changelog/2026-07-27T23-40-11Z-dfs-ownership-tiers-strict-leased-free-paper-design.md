# DFS ownership tiers: strict/leased/free paper design

Added `distributed-sync/OWNERSHIP.md`: a third ownership tier ("leased" — durable/replicated ciphertext, key-gated and revocable by the owner) alongside strict/free, plus a worked storage-space scenario showing access-tier and storage-contribution as orthogonal axes. Resolves, on paper only, the strict-revocability-vs-durable-storage tension both `upload-and-share/OWNERSHIP.md` and `distributed-sync/TODO.md` had flagged but left undesigned. Pillar 1 per VISION.md's reaffirmed scope — doesn't change the current one-server strict/free build.

- **Doc size** (Unicode codepoints): `distributed-sync/OWNERSHIP.md` 0 → 5365 (new); `distributed-sync/README.md` 1754 → 2007; `distributed-sync/TODO.md` 1834 → 2041; `upload-and-share/OWNERSHIP.md` 6274 → 6509.
