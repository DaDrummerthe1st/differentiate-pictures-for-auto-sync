# Asked inline instead of using AskUserQuestion for a real user decision

See [README.md](../README.md) for what belongs here.

## What happened

While debugging the redundant chunk-title issue in the mamma-photo-viewer GUI (album header and its "loose files" chunk showing identical text back-to-back), this session ended a reply with plain running text - "Want me to fix that specifically...?" - instead of calling `AskUserQuestion`, even though this was exactly the kind of genuinely user-owned decision (fix now vs. defer) that global CLAUDE.md's "Questions go through the popup UI, not running text" rule covers. Joakim caught it and asked why the tool wasn't used, and asked for this repo's documentation to be corrected accordingly.

Verbatim, what this session said in response before correcting course (kept here rather than paraphrased, at Joakim's request):

> You're right — I asked "Want me to fix that specifically...?" as running text instead of AskUserQuestion, which is exactly the global rule I should have followed. Let me first actually ask it correctly, then log this as a process lapse per this repo's convention.

## Why it happened

The question felt like a small, low-stakes offer tacked onto the end of a factual explanation, which made it easy to phrase as a natural sentence rather than pausing to route it through the tool - but "small" isn't the test the rule uses; "is this the user's call to make" is, and this one clearly was.

## What changed

No new CLAUDE.md rule added - the existing global rule already covers this exactly and this project's CLAUDE.md deliberately doesn't restate content that's already documented elsewhere (its own "lean, exact, compact" principle). Behavioral correction only: any reply ending in an offer/choice that's genuinely the user's to make goes through `AskUserQuestion`, regardless of how small or naturally-phraseable the question feels in the moment - re-asked correctly via the tool immediately after this was caught, in the same conversation.
