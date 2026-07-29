# TODO — income

Everything below was raised 2026-07-29 during a tag/sharing/security/DFS design session, moved here from `distributed-sync/TODO.md` and `upload-and-share/TODO.md` (not redesigned, not redecided — a relocation for a topic those files don't really own).

## Rollout timeline — the "when/for whom" behind VISION.md's four Pillars

Joakim's own three-version rollout plan, captured verbatim so it isn't lost before a proper [../VISION.md](../VISION.md) pass folds it in as that file's own "rollout phases" framing (distinct from the four Pillars, which describe *what* gets built, not *when*/*for whom*):

- **V1**: a service for 2-3 people, mostly to observe *how* they actually use it — are they naming pictures, sharing outside the group, marking people/objects, etc. (everything `prototypes/mockup/` demonstrates). Also run and save AI model output on every picture: object detection, picture quality, venue guessing, feelings/emotions, etc.
- **V2**: those 2-3 people get their own NAS/router each. Their day-to-day experience should be unchanged — the DFS work in `../distributed-sync/` (`OWNERSHIP.md`/`METADATA.md`/`TODO.md`) happens behind the scenes. This is where centralization-vs-decentralization decisions and load-balancing actually get built, not before.
- **V3**: commercialize — sell NAS/routers, keep developing the system. Needs slow, organic growth to find/fix problems, since the overhead budget at this stage will be very small if any exists at all.
- **This is explicitly not a small family-style network long-term** — the stated long-term goal is a service used by "everyone," with the concrete example of an AI curating the best photos/a photo-flow from an audience of 65,000 people at a large public event. `../VISION.md`'s existing Pillar 3 (event/party mode) already gestures at this; this note makes the eventual *scale* explicit rather than implicit. (Note, resolved 2026-07-29: this doesn't mean cross-network face-matching needs a harder mechanism at that scale — see `../distributed-sync/METADATA.md`, access, not scale, is what bounds that search.)
- **Not started**: folding this into `../VISION.md` properly. Flagged so it survives to whichever session picks it up.

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
- A marketplace pulls in real obligations a pure sharing model never triggers: payment-facilitation (Stripe Connect is the standard industry pattern specifically because it absorbs the money-transmission-licensing burden) and tax reporting/collection on sales. **This project only needs to account for Swedish tax law** (Skatteverket reporting rules, Swedish/EU moms (VAT) on digital-goods sales) — see [../policies/POLICY.md](../policies/POLICY.md)'s Jurisdiction section — not the US Form 1099-K/marketplace-facilitator-law citations an earlier research pass mistakenly used; that research thread needs redoing against Swedish/EU sources specifically before this is ever scoped for real. The US findings are recorded here only as a still-useful illustration of *what categories* of obligation a marketplace triggers, not as the applicable rules.
- Still not scoped or designed — a price/for-sale attribute layered onto the existing ownership tiers ([../distributed-sync/OWNERSHIP.md](../distributed-sync/OWNERSHIP.md)) is the likely shape if ever pursued, reusing the entity/ownership provenance chain already being built, but this is a future call.

## Storage-contribution incentive

Joakim's own sketch for what makes contributing spare storage worthwhile: your device has to store DHT/routing data proportional to how much space you're sharing (to earn back a portion of network storage in return). Open questions he raised, verbatim: for a node sharing *all* of its spare space, the durability benefit ("my files keep existing even if my own hardware fails") has to outweigh the simpler alternative of just keeping photos on a phone plus a home RAID array — otherwise there's no real incentive to join the network at all. Also: how long should a photo survive "in the cloud" (on other people's nodes) after the contributing node itself goes offline, since every extra timeslot is pure overhead for the rest of the network once the original owner's hardware is gone? Raised formula sketch, unrefined: `% ROI = time × your cloud files` (or similar) — not a designed mechanism, captured so the idea isn't lost. Connects to [../distributed-sync/TODO.md](../distributed-sync/TODO.md)'s DHT/PoW/PoS/PoUW research and to Filecoin/Storj's proof-of-continued-storage mechanisms already researched there.

## Status

Opened 2026-07-29.
