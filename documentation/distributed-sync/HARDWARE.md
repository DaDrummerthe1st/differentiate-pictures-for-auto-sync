# Hardware — the NAS/router device Pillar 1 eventually ships

Not a committed design — see [README.md](README.md) and [../VISION.md](../VISION.md)'s Rollout phases (V2 "each person gets their own NAS/router", V3 "commercialize — sell NAS/routers"). This file exists so the hardware direction Joakim has already thought through isn't lost before V2/V3 actually start. Distinct from [../photo-server/HARDWARE.md](../photo-server/HARDWARE.md), which documents the machine currently *hosting* the app today — this file is about the device the project would eventually sell to end users.

**Neither generation below is deployed. Corrected 2026-08-07** — an earlier version of this file wrongly stated v1 was "actually running today"; see [../bugs/claude-bugs/under_process/2026-08-07-claimed-rpi3-nas-router-hardware-is-currently-running-without-verifying-against-actual-deployed-hardware.md](../bugs/claude-bugs/under_process/2026-08-07-claimed-rpi3-nas-router-hardware-is-currently-running-without-verifying-against-actual-deployed-hardware.md) for the correction. **What's actually running today**: a limited-functionality prototype on Joakim's homeserver — the i5-650 desktop-class machine documented in [../photo-server/HARDWARE.md](../photo-server/HARDWARE.md), not RPi3-class hardware, and not configured as a NAS+router. Both v1 and v2 below are future plans, not a current-vs-future pair.

## Two generations, raised 2026-08-06

**v1**: Raspberry Pi 3 class hardware acting as NAS + small router (two network interfaces), per [README.md](README.md)'s existing vision. Cheap, off-the-shelf, easy to source, well-documented software ecosystem. Nothing built yet — this is the nearer-term, simpler of the two future generations, not something already deployed.

**v2 — a speculative, specially-built successor**, not yet designed, captured here so the idea isn't lost: a custom PCB, GPU-capable board (needed for on-device AI inference — object/face detection, embeddings — per [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s detector work), hot-swappable SSD bays, and a modular design that includes a 5G modem module, aimed at "complete customizability." Explicitly framed by Joakim as "ver2 of the hardware" — v1 (RPi3-class) is the nearer-term baseline this direction would build on once started; v2 is a later, harder, more expensive undertaking, not a prerequisite for V2/V3 of the rollout plan.

## End-goal architecture: user hardware plus a central server, raised 2026-08-07

Not a redesign of [../VISION.md](../VISION.md)'s Pillar 1 — a clarification of it, folded in there too. The end goal is **not** a purely peer-to-peer network with no central component: most actions run on each user's own hardware (v1/v2 above, per Pillar 1's DFS), but a central server persists alongside it, holding **global metadata and predictions about global user behavior that are not PII** — e.g. aggregate patterns learned across the whole user base, not any individual's own photos or identifying data. This is consistent with, and gives a concrete shape to, [../VISION.md](../VISION.md) Pillar 2's already-existing line about the system "learn[ing] globally across the network and personaliz[ing] per user" — that global-learning component is what the central server would hold. Not yet designed (what exactly counts as non-PII global signal, how it's aggregated without leaking individual behavior, where this server lives/who operates it) — captured here so the hybrid (not fully-decentralized) shape isn't lost before Pillar 1 design actually starts.

## Market precedent for the v2 direction — researched 2026-08-06

None of these are proposed as *the* vendor/partner — captured as evidence the shape (modular, hot-swap, open) is a real, viable market segment, not a novelty:

- **ZimaBoard / ZimaCube** (https://www.zimaboard.com/) — open-source single-board server line; ZimaCube specifically ships a hot-swappable multi-bay design (start with a few drives, add more later) plus PCIe expansion for NVMe/AI-accelerator add-ons. ZimaBoard 2 crowdfunded on Kickstarter, shipped 2025. Closest existing product to this project's v2 hot-swap-SSD idea.
- **Turing Pi 2** (https://turingpi.com/) — modular compute-module carrier board (swap in different SoM types); raised $1M on Kickstarter in a single day (Tom's Hardware). Evidence a modular, buy-your-own-modules board can generate real demand fast.
- **Pine64** (https://pine64.org/) — company builds the hardware, community builds the software; ships in small batches (tens/hundreds) at low prices, invites community feedback before mass production. A precedent for how an open-hardware company can stay solvent without pretending to be a mass-market consumer brand from day one.
- **GL.iNet / OpenWrt-class routers and Intel N100 mini-PCs** — the current baseline hobbyists compare any new open router/NAS device against; sets the low end of price/performance expectations a v2 device would be judged against even though it's aimed at a different (higher-spec) tier.

None of the above include a 5G modem as a modular component — that piece appears to be a genuine differentiator with no close existing precedent found in this research pass, not a gap in the search.

## Design impression — non-negotiable regardless of which generation ships

Raised 2026-08-06, applies to v1, v2, and anything between: **the physical device must read as small-footprint and well-designed to two very different audiences at once** — people who read a spec sheet and care about the chipset, and people who will never open a terminal and just want something unobtrusive on a shelf. Researched 2026-08-06: industrial-design coverage of consumer electronics consistently frames this as the actual lever that moves a product from a niche/enthusiast audience to a mainstream one — good industrial design turns a technically-capable box into something a non-technical buyer would choose to have visible in their home, and is what building genuine brand loyalty (not just a one-time sale) is reported to hinge on. Concretely: this rules out anything that reads as "beige box PC" or "server-room gear" regardless of what's inside it, for either hardware generation.

## Status

Opened 2026-08-06, capturing Joakim's v1/v2 framing plus a same-day market/design research pass. Nothing here is scheduled — this is pre-V2 groundwork per [../VISION.md](../VISION.md)'s Rollout phases. Business/profitability angle (crowdfunding, community, warranty) captured separately in [../income/TODO.md](../income/TODO.md), not repeated here. **2026-08-07**: corrected the false "v1 is currently running" claim (see the note at the top of this file) and added the end-goal user-hardware-plus-central-server architecture clarification above.

**Before describing anything in this file as "currently running" or "deployed": check [../photo-server/HARDWARE.md](../photo-server/HARDWARE.md) (the one doc that documents actually-deployed hardware) or ask Joakim directly — never infer current deployment status from this file's or [README.md](README.md)'s vision-style prose.**
