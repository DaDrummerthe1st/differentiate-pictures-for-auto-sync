# Assumed instead of asked on an ambiguous instruction

## What happened

Joakim wrote "DO NOT WRITE ANYTHING IN LOCAL STORAGE for claude!!" and it was read as being about browser `localStorage` in the photo-viewer app (since that word had just appeared in a bugs/TODO.md write-up). He actually meant something different: not persisting durable instructions only to the AI's own local/private memory instead of the repo. This produced a POLICY.md addition and a bugs/TODO.md edit that then had to be fully reverted once he clarified.

## Why it happened

The emphatic, all-caps phrasing read as urgent enough to act on immediately, and "localStorage" had a recent, literal, plausible match in context (my own just-written suggestion) - that surface-level match was trusted over checking whether it actually fit what was being reacted to.

## What changed

None yet as a concrete rule change. This project's own non-negotiable is "ask or search, never guess" for uncertain facts - logged here as a practice to explicitly extend that instinct to ambiguous *instructions* under time pressure too, not just uncertain facts, especially for anything that writes to a policy file. A single clarifying question would have cost less than the write-then-revert cycle.
