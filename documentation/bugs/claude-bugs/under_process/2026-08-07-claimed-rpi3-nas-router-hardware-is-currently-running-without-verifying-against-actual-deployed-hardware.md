# Claimed RPi3 NAS/router hardware is currently running without verifying against actual deployed hardware

See [README.md](../README.md) for what belongs here.

## What happened

While writing `documentation/distributed-sync/HARDWARE.md` (2026-08-06), this session stated: "v1 — what's actually been used so far: Raspberry Pi 3 class hardware acting as NAS + small router... This is the generation actually running today, not a future plan." This was wrong on every count: no RPi3/NAS/router device is deployed anywhere. What actually runs is a limited-functionality prototype on Joakim's homeserver — an old i5-650 desktop-class machine (see [../../photo-server/HARDWARE.md](../../photo-server/HARDWARE.md)), not RPi3-class hardware, and not configured as a NAS+router at all. Joakim corrected it directly: "This is not running atm. It is also a future plan... What is running now is a prototype with very little of the functionality. This runs on my homeserver."

## Why it happened

[distributed-sync/README.md](../../distributed-sync/README.md)'s existing vision paragraph describes the target device in present-tense-sounding, aspirational language ("Each user runs their own device at home as a NAS... anything from a Raspberry Pi up") with its "nothing here is built yet" qualifier sitting one sentence above rather than inside that sentence itself. When drafting HARDWARE.md, this session paraphrased that vision prose into a "v1 = what's running now" framing without cross-checking it against the one doc that actually documents currently-deployed hardware ([photo-server/HARDWARE.md](../../photo-server/HARDWARE.md), an i5-650 desktop, not a Pi). This is exactly the case [WORKFLOW.md](../../policies/WORKFLOW.md)'s "Ask or search" rule covers — current deployment status is project-specific fact, not something to infer from a vision paragraph — and it wasn't applied: inferred instead of checked.

## What changed

Corrected `distributed-sync/HARDWARE.md` to state plainly that v1 is not deployed — it's a future plan, like v2, differing only in being closer to already-used pieces — and that the real current state is a limited prototype on the homeserver documented in `photo-server/HARDWARE.md`. Added an explicit warning to `distributed-sync/HARDWARE.md`'s own Status section (mirroring the precedent already set in `photo-server/HARDWARE.md`'s "don't infer which host you're on... check the IP or ask" line): any future edit describing this project's hardware as "currently running" must cross-check `photo-server/HARDWARE.md` — the one doc that documents actually-deployed hardware — or ask, never infer from vision-style prose in a README.
