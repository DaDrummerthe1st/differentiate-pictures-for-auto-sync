# differentiate-pictures-for-auto-sync

Since Google started counting every picture against the Google One quota — limiting how many photos you can take before you have to go back and delete some — this project handles pictures and movie clips so the user owns the information and the metadata, not a cloud provider.

The overall idea: preserve and help rediscover old, forgotten pictures and movies, while categorising them for future AI assistance, tuned to each user's individual preferences.

## Status

**2026-09-05**: clean slate — no live application code right now. Every previous implementation
(a browser-based multi-user photo server, a local photo-differentiation/quality/object-detection
pipeline with a findings viewer, a contacts-import library) is kept as design reference under
[previous-work/](previous-work/README.md), not deleted, but none of it runs or is built on
today. The project just pivoted from a phone-viewable PWA toward a native Android app (on-device
photo handling before any server round-trip, automatic background sync — no browser API reaches
that); see [documentation/VISION.md](documentation/VISION.md)'s 2026-09-05 note. Next session
scopes the native app itself.

## Features (vision)

- **Sort / delete files** — discard, save, flag, or even mark custom objects within a picture or movie clip.
- **Learn each user's preferences** via AI, following the patterns set above.
- **Sync and save pictures securely**, owned by the user.
- **Shared syncing** — dedicate some disk space to the network (globally or to a chosen set of friends) in exchange for storage elsewhere on the network, all access-controlled so only people the user chooses can see their files.

## Documentation

Full documentation, working agreement, and open TODOs live in [documentation/](documentation/README.md). Start there — this file is just the pitch.
