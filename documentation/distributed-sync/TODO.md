# TODO — distributed-sync

Nothing is designed or built yet. Captured so far, from early notes and
the initial documentation session:

- Sync between devices (general, PC-to-PC).
- Android → PC sync over local WLAN.
- Android → PC sync over WAN.
- Phone app gesture UX: swipe left = discard, right = save, down = mark,
  up = undo.
- On mobile devices not yet synced with the server: rename discarded
  files so common gallery apps don't surface them; keep a local temp
  database of choices and sync it once connectivity is available.
- Self-hosted NAS device spec — see [README.md](README.md) for the full
  vision as described so far.
- Shared/distributed file system where users can dedicate spare storage
  and AI compute in exchange for shared access — architecture not yet
  decided.

**Open question**: full roadmap addendum for this phase, to be provided
by Joakim in a future session. Don't design against the vision in
README.md as if it were final.
