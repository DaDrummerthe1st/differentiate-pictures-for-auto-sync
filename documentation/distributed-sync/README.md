# distributed-sync/

Future work: getting pictures/movies off a single machine and onto a
system the user owns and controls, without relying on a quota-limited
cloud provider. Nothing here is built yet — see [TODO.md](TODO.md).

## Vision (high-level, not a committed design)

Each user runs their own device at home as a NAS — open-source and
hardware-agnostic (anything from a Raspberry Pi up), acting as a small
router (two network interfaces) plus a file system, reachable from the
internet. Users can optionally dedicate spare storage and compute to a
shared distributed file system (torrent-network style), gaining access to
some shared cloud storage and AI compute in return — similar in spirit to
volunteer-computing projects like SETI@home, but for storage/AI
resourcing instead of signal analysis. The bottom line is autonomy: no
single point of dependency on a third-party quota.

Not yet a committed design — see [TODO.md](TODO.md)'s open question for
what's still unresolved.

## Relevant external tools

Not adopted yet.

| Project | Site | Purpose |
| --- | --- | --- |
| SyncThing | https://syncthing.net/ | Continuous sync between units |
| rClone | https://blog.rymcg.tech/blog/linux/rclone_sync/ | Auto-sync of files via bash |
