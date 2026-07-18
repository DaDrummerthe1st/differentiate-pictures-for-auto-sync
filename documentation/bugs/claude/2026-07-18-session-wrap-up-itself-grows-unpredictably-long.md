# Session wrap-up itself grows unpredictably long

Not quite the usual shape for this folder (a routine that didn't run, or
an unchecked claim) - this is a process observation Joakim raised
directly: session wrap-up itself doesn't reliably terminate. See
[README.md](README.md) for the general pattern this folder covers.

## What happened

2026-07-18: Joakim explicitly asked to wrap up a very long session. The
formal wrap-up routine ran (doc-drift sweep, loose ends, stale TODOs,
final test suite, commit_cost coverage, CHANGELOG entry) and was
announced complete. The session then continued substantively for a long
stretch afterward anyway - some of it legitimate (the wrap-up sweep
itself surfacing a stale Swagger-status doc and an unfulfilled promise
that both needed fixing), but much of it genuinely new ideas arriving
*because* the wrap-up conversation itself prompted them (the iteration-
vs-session-cadence question, the vendor-lock-in policy, the tags schema
discussion). Joakim named the actual cost plainly: time spent extending
wrap-up is time not spent on production work actually making the GUI
operate as it should.

## Why it happened

No boundary rule distinguishes "the wrap-up sweep found something that
needs fixing before this session can honestly be called done" (worth
finishing) from "a new idea occurred to Joakim while wrap-up was
happening, unrelated to what the sweep itself surfaced" (arguably
belongs in a fresh session, not this one). Every new substantive
message got engaged with fully and immediately, the same way it would
mid-session, with nothing signaling "we're in the wrap-up phase, new
ideas get logged for later rather than actioned now."

## What changed

Not resolved as a hard rule yet - this is a case where the actual fix
needs Joakim's input (he's the one bringing the new ideas; this isn't
purely a Claude-side discipline issue the way the other entries in this
folder are). Captured here as an explicit input to the "iteration vs.
session cadence" discussion already deferred to a new session (see the
discussion prompt given to Joakim earlier 2026-07-18): that discussion
should also decide whether wrap-up needs its own scope boundary - e.g.
"once wrap-up is announced complete, a new idea that isn't something the
sweep itself surfaced gets logged as a backlog item, not actioned in the
same session" - rather than leaving wrap-up's length as unbounded as the
session itself.
