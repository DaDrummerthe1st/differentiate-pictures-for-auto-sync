# Hardware — the NAS/router device Pillar 1 eventually ships

Not a committed design — see [README.md](README.md) and [../VISION.md](../VISION.md)'s Rollout phases (V2 "each person gets their own NAS/router", V3 "commercialize — sell NAS/routers"). This file exists so the hardware direction Joakim has already thought through isn't lost before V2/V3 actually start. Distinct from [../photo-server/HARDWARE.md](../photo-server/HARDWARE.md), which documents the machine currently *hosting* the app today — this file is about the device the project would eventually sell to end users.

## Two generations, raised 2026-08-06

**v1 — what's actually been used so far**: Raspberry Pi 3 class hardware acting as NAS + small router (two network interfaces), per [README.md](README.md)'s existing vision. Cheap, off-the-shelf, easy to source, well-documented software ecosystem. This is the generation actually running today, not a future plan.

**v2 — a speculative, specially-built successor**, not yet designed, captured here so the idea isn't lost: a custom PCB, GPU-capable board (needed for on-device AI inference — object/face detection, embeddings — per [../curation/ARCHITECTURE.md](../curation/ARCHITECTURE.md)'s detector work), hot-swappable SSD bays, and a modular design that includes a 5G modem module, aimed at "complete customizability." Explicitly framed by Joakim as "ver2 of the hardware" — v1 (RPi3-class) remains the baseline being used and refined now; v2 is a later, harder, more expensive undertaking, not a prerequisite for V2/V3 of the rollout plan.

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

Opened 2026-08-06, capturing Joakim's v1/v2 framing plus a same-day market/design research pass. Nothing here is scheduled — this is pre-V2 groundwork per [../VISION.md](../VISION.md)'s Rollout phases. Business/profitability angle (crowdfunding, community, warranty) captured separately in [../income/TODO.md](../income/TODO.md), not repeated here.
