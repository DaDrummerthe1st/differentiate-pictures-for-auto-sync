# Promised a follow-up mid-conversation without tracking it as a todo

A routine that should have run per an existing rule, and didn't - or a
claim made without properly checking it first. See
[README.md](README.md) for what belongs here.

## What happened

After Joakim answered the three design questions for the
pre-compile-thumbnails feature, I said (in prose) that I'd synthesize
his answers into a concrete design and present it back for confirmation
before building. That synthesis work happened internally, but the
"present it back" step never actually reached Joakim - not until the
session's wrap-up sweep, several dozen messages later, found it as an
unresolved loose end and wrote it into the bug report at that point.
Joakim asked directly why this wasn't done at the time of the
discussion.

## Why it happened

Immediately after Joakim's answers arrived, several unrelated messages
arrived in quick succession (a security-testing question, a
CVE-monitoring feature request, and then - critically - a live "no
thumbnails loading" incident that escalated into a publicly-exposed
Swagger/OpenAPI vulnerability, which consumed all near-term attention
for a good while). The promise to "present this back for confirmation"
was only ever stated in response prose - it was never converted into a
`TodoWrite` item. `TodoWrite` exists specifically to hold open work
across exactly this kind of interruption; it wasn't invoked at the
moment the promise was made. Once the live emergency passed, the
conversation moved into a long stretch of other topics with nothing
forcing a look-back at earlier unfulfilled promises - the only thing
that actually surfaced it was the wrap-up routine's explicit "scan for
loose ends" step, run much later.

This is a real, well-specified mechanism, not a vague "got confused":
a soft verbal promise made in prose is invisible to any later self-check
unless it's also recorded as a structured, trackable item.

## What changed

New CLAUDE.md rule (Non-negotiables): whenever a reply promises a
follow-up action for later in the same conversation ("I'll present this
for confirmation," "I'll come back to this," "let me get back to you on
X"), add a `TodoWrite` item for it in that same turn, not just state it
in prose. A promise that only exists as text is invisible to any later
self-check; a tracked item survives interruptions.
