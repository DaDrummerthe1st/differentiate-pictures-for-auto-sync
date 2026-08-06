# TODO — income

Everything below was raised 2026-07-29 during a tag/sharing/security/DFS design session, moved here from `distributed-sync/TODO.md` and `upload-and-share/TODO.md` (not redesigned, not redecided — a relocation for a topic those files don't really own).

## Rollout timeline — the "when/for whom" behind VISION.md's four Pillars

**Folded into [../VISION.md](../VISION.md)'s own "Rollout phases" section, 2026-07-29** — not repeated here.

## Revenue ideas

- **A percentage cut of sold photos** — ties to the marketplace idea below.
- **Selling a user's unused/shared DFS storage space to others**, with a small profit margin to "the DPFAS owner company" (not yet registered as a real legal entity).
- **Event-space rental**: an event host pays a fee for the event-hosting service itself (e.g., "x SEK for the pictures your guests sent in"), so guests attending the event never need individual DPFAS accounts, and existing users who share photos into the event don't lose any of their own personal storage quota to it. Ties to [../upload-and-share/EVENTS.md](../upload-and-share/EVENTS.md)'s already-resolved "event's own dedicated account owns free-for-all uploads" decision.
- **Pre-installed "it just works" hardware**: alongside the modular, buy-your-own-upgrades hardware vision (`../distributed-sync/TODO.md`'s IPFS-alternatives note), a pre-configured device for users who don't want to think about it is itself a candidate income stream.

## Marketplace — letting users sell photos through the network

Researched 2026-07-29, not designed. Real precedent exists but none maps directly onto "sell photos over a family-style/DFS network":

- Filecoin/Storj solve *paid storage capacity* (on-chain escrowed deals or a token/satellite payout model), not content licensing.
- Adobe Stock/Shutterstock/Unsplash+ solve licensing/payout but are fully centralized, no distributed-storage or blockchain element at all.
- The closest blockchain-native attempt at "photo rights + token" — **KodakCoin/KODAKOne (2018)** — is a clear cautionary tale: SEC scrutiny, Kodak had zero actual operational control despite being the public face, collapsed by 2019-2020. The broader NFT-art market (which some photographers did try) fell roughly 90% from its 2022 peak; a respected photography-criticism retrospective (Aperture) frames the wave of photographer adoption as driven by a depressed print market rather than the technology solving a real problem.
- A marketplace pulls in real obligations a pure sharing model never triggers: payment-facilitation and tax reporting/collection on sales. **This project only needs to account for Swedish tax law** (Skatteverket reporting rules, Swedish/EU moms (VAT) on digital-goods sales) — see [../policies/POLICY.md](../policies/POLICY.md)'s Jurisdiction section — not the US Form 1099-K/marketplace-facilitator-law citations an earlier research pass mistakenly used; that research thread needs redoing against Swedish/EU sources specifically before this is ever scoped for real. The US findings are recorded here only as a still-useful illustration of *what categories* of obligation a marketplace triggers, not as the applicable rules.
- Still not scoped or designed — a price/for-sale attribute layered onto the existing ownership tiers ([../distributed-sync/OWNERSHIP.md](../distributed-sync/OWNERSHIP.md)) is the likely shape if ever pursued, reusing the entity/ownership provenance chain already being built, but this is a future call.

## Storage-contribution incentive

Joakim's own sketch for what makes contributing spare storage worthwhile: your device has to store DHT/routing data proportional to how much space you're sharing (to earn back a portion of network storage in return). Open questions he raised, verbatim: for a node sharing *all* of its spare space, the durability benefit ("my files keep existing even if my own hardware fails") has to outweigh the simpler alternative of just keeping photos on a phone plus a home RAID array — otherwise there's no real incentive to join the network at all. Also: how long should a photo survive "in the cloud" (on other people's nodes) after the contributing node itself goes offline, since every extra timeslot is pure overhead for the rest of the network once the original owner's hardware is gone? Raised formula sketch, unrefined: `% ROI = time × your cloud files` (or similar) — not a designed mechanism, captured so the idea isn't lost. Connects to [../distributed-sync/TODO.md](../distributed-sync/TODO.md)'s DHT/PoW/PoS/PoUW research and to Filecoin/Storj's proof-of-continued-storage mechanisms already researched there.

## Reaching profitability early, even while open source — raised 2026-08-06

Joakim's own framing: it matters to see a profit reasonably soon, even though both the hardware ([../distributed-sync/HARDWARE.md](../distributed-sync/HARDWARE.md)) and software stay open source. Three specific levers he named, plus what researched precedent (2026-08-06) says about each:

- **Community feeling** — Pine64's model (hardware run by a company, software crafted by the community, small early batches, feedback solicited before mass production) is direct precedent that "open source" and "a company that stays solvent" aren't in tension, provided the company doesn't try to act like a conventional closed-source consumer brand from day one.
- **The torrent-base** — [../distributed-sync/README.md](../distributed-sync/README.md)'s DFS network itself (users contributing spare storage/compute) doubles as the thing that makes early adopters invested co-owners of the network rather than customers of a product, which is the same dynamic crowdfunding/open-hardware platforms rely on: Crowd Supply's own founder is on record framing crowdfunding and free software as pulling from the same pool of idealism-plus-personal-interest motivated people. Concretely, this suggests: pre-order/crowdfund the v2 hardware once it's real enough to specify, rather than self-funding a full production run up front — Turing Pi 2 raising $1M in a single day on Kickstarter, and ZimaBoard 2 crowdfunding its way to a 2025 ship date, are both evidence a modular/open NAS-class board can generate real pre-committed demand before a single unit is manufactured.
- **The guarantee** — Sweden's *Konsumentköplagen* already gives buyers of anything sold new a minimum 3-year statutory right to complain about an original/manufacturing defect, regardless of whether the seller offers any voluntary warranty on top, and the burden of proof sits with the seller (not the buyer) throughout that window (researched 2026-08-06, Konsumentverket). This is not something the project can shorten or opt out of by being small, open source, or crowdfunded — it applies the moment a physical unit is sold as new to a consumer in Sweden. Worth treating as a cost input to any hardware price/margin plan, not an optional nice-to-have selling point (though it can also be marketed as one, since it's a stronger guarantee than many established consumer electronics brands offer as a *voluntary* term).

None of this is a committed monetization plan — captured so the "how do we get to profit soon without abandoning open source" framing isn't lost before V3 (commercialize) actually starts, per [../VISION.md](../VISION.md)'s Rollout phases.

## Status

Opened 2026-07-29. 2026-08-06: added the early-profitability/community/torrent-base/warranty section above.
