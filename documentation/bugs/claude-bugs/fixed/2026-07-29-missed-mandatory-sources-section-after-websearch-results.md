# Missed mandatory Sources section after WebSearch results

See [README.md](../README.md) for what belongs here.

## What happened

Ran three `WebSearch` calls (Netflix/DRM, XMP vs. EXIF, blockchain/DHT) during tag/sharing design work and synthesized the results into a design reply, but never included the "Sources:" section the tool's own description marks as a **mandatory, CRITICAL requirement** ("This is MANDATORY - never skip including sources in your response"). Caught only because Joakim asked directly, mid-conversation, for the sources used so he could evaluate their quality — not caught by any self-check on my part before that.

## Why it happened

Treated the search results as raw material to fold into a synthesized answer (consistent with this project's own "lean, exact, compact" documentation style) and lost track of the tool's own separate, explicit output-format requirement in the process — prioritized producing a clean narrative answer over satisfying a hard requirement stated directly in the tool description I'd just read.

## What changed

Immediately supplied the sources retroactively once asked, and included them going forward for the rest of this session's research (the background research agent dispatched afterward was explicitly instructed to report full source lists). No CLAUDE.md rule change made — this is a tool-usage requirement stated in `WebSearch`'s own description, not a gap in this repo's docs — logged so a future session double-checks tool-mandated output requirements (not just this project's own rules) before sending a reply that uses that tool's results, especially when several tool calls are batched together and it's easy to synthesize past the requirement.
