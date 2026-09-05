# Claimed no demo server was running based on a pgrep check that only matched its own invoking shell command

See [README.md](../README.md) for what belongs here.

## What happened

Earlier in this session, `python3 -m contacts.demo.server` was started (with permission) to verify the
`/parse` endpoint, then supposedly killed with `kill $SERVER_PID; wait $SERVER_PID`. When Joakim later
asked "is it reset?", the check run was:

```
pgrep -af "contacts.demo.server" || echo "no demo server running"
```

This returned a line that *looked* like a match, but was actually the Bash tool's own eval-wrapper
shell command (the harness runs commands via `bash -c 'eval "<command>" ...'`, and that wrapper's
command line literally contains the search text `"contacts.demo.server"` because that's the pattern
being searched for). `pgrep -af` matches on the full command line by design, so it matched itself. The
follow-up `lsof -i :8765`/`ps aux | grep 8765` check in that same turn reported "port 8765 free" — but
that was run *before* a genuine second server (started for a later verification pass) was ever
launched, not proof the first one was gone. Joakim was told "No demo server is running... nothing of
mine is left running", stated as fact without it actually being re-verified at that moment. The real
process (PID 368872) kept running, undetected, for the rest of the session until a *different*
`contacts.web.server` instance tried to bind port 8765 and failed with `OSError: Address already in
use` — that crash, not any check, is what surfaced the leftover process.

## Why it happened

Two compounding mistakes: (1) trusting `pgrep -af PATTERN` as a liveness check without accounting for
the harness's own command-wrapping making the pattern match the checking command itself — a
self-referential false positive that doesn't happen with a plain naked shell; (2) stating "is it
reset?" was answered by that check's output without registering that the output was suspicious (a
`pgrep` on a server process should never print a `bash -c 'eval ...'` line — that shape alone should
have triggered doubt) and without cross-checking with a mechanism immune to this failure mode, like a
port-bind check via `lsof -i :PORT` (exit code 1 with no output = genuinely free) run *after* the fact,
not reused from an earlier, differently-scoped check in the same turn.

## What changed

Going forward, verifying "is a background process/port really free" uses `lsof -i :<port>` (or
`fuser <port>/tcp`) checked by exit code / empty output, never `pgrep -af <pattern>` when the search
pattern could plausibly appear in the Bash tool's own wrapped invocation text (which it will, any
time the pattern is a literal string being grepped for, since the harness's `eval` wrapper embeds the
whole command including that literal). When a liveness/port check's output looks unusual (e.g. a
`pgrep` result showing an `eval`/`bash -c` wrapper line instead of the target process's own command),
treat that as a signal the check itself is broken, not as evidence either way, and rerun with a
different mechanism before reporting a result to Joakim as fact.
