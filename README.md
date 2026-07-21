# differentiate-pictures-for-auto-sync

Since Google started counting every picture against the Google One quota — limiting how many photos you can take before you have to go back and delete some — this project handles pictures and movie clips so the user owns the information and the metadata, not a cloud provider.

The overall idea: preserve and help rediscover old, forgotten pictures and movies, while categorising them for future AI assistance, tuned to each user's individual preferences.

## Status

The photo-viewer GUI (`app/`) is the live, working piece — see [documentation/gui/README.md](documentation/gui/README.md) for what it is, how to run it, and its current feature set; [documentation/gui/TODO.md](documentation/gui/TODO.md) for open work. The original file-differentiation/sort tool (object detection, MySQL-backed dedup) lives on as a prototype/reference for the planned server-side analysis backend — see [prototypes/differentiate_pictures/](prototypes/differentiate_pictures/).

## Features (vision)

- **Sort / delete files** — discard, save, flag, or even mark custom objects within a picture or movie clip.
- **Learn each user's preferences** via AI, following the patterns set above.
- **Sync and save pictures securely**, owned by the user.
- **Shared syncing** — dedicate some disk space to the network (globally or to a chosen set of friends) in exchange for storage elsewhere on the network, all access-controlled so only people the user chooses can see their files.

## Documentation

Full documentation, working agreement, and open TODOs live in [documentation/](documentation/README.md). Start there — this file is just the pitch.
