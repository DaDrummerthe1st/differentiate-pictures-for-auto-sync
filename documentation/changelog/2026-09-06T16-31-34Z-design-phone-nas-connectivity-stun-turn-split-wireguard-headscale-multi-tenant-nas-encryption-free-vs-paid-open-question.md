# Design phone-NAS connectivity (STUN/TURN split, WireGuard/Headscale), multi-tenant NAS encryption, free-vs-paid open question

Continuing the native-app networking discussion. `distributed-sync/README.md` gets a new
"Phone ↔ NAS connectivity" section: WireGuard (tunnel) + Headscale (self-hosted, STUN-equivalent
rendezvous only) as the free default, coturn/Stuntman named for STUN/TURN, with a 2026-09-06
web-search-verified fact grounding the design — free public STUN exists, free public TURN
effectively doesn't (bandwidth cost), confirming TURN-equivalent relay as the correct place for a
paid, opt-in tier rather than STUN. `OWNERSHIP.md` extends the existing "leased" tier to multiple
people sharing one physical NAS (each tenant needs her own key-gated encrypted volume) and flags a
real gap the encryption doesn't cover: confidentiality vs. availability when a box lives at a
friend's house. `income/TODO.md` records the genuinely open question Joakim raised: connectivity
is always free for buyers of this project's own hardware, undecided for FOSS-only self-hosters
given real ongoing coordination-server costs.

- **Doc size** (Unicode codepoints): `documentation/distributed-sync/README.md` 5,667 → 8,439 (+2,772); `documentation/distributed-sync/OWNERSHIP.md` 5,365 → 6,701 (+1,336); `documentation/income/TODO.md` 7,450 → 8,295 (+845).
