# Didn't create bug report at investigation-open, only when asked if progress was saved

A routine that should have run per an existing rule, and didn't - or a claim made without properly checking it first. See [README.md](README.md) for what belongs here.

## What happened

Joakim reported a live bug ("clicked a picture, it couldn't be shown") and this session spent several turns actively investigating it - checking the deployed code, re-reading the DOM-unload/lightbox-index refactor, asking for DevTools evidence - without ever creating the required bug report file. Joakim had to ask "is the progress for this bug saved?" before the file got created at all, at which point the investigation was written up retroactively rather than having accumulated in the file as it happened.

## Why it happened

The rule ("bug/incident files start at investigation-open, not fix-time... a session cut off mid-investigation must still leave a trail") is explicit and was already known - this session even cited it correctly once asked. The lapse was purely about *when* to act on it: treating "let me first understand what's happening" as a reason to delay filing, rather than filing immediately and updating the file as understanding develops. This is the same underlying pattern the rule itself was written to prevent (a session ending mid-investigation with no trail), just not triggered by a session cutoff this time - triggered by simply not pausing to file before diving into the technical back-and-forth.

## What changed

No new rule - the existing one is unambiguous and was already being correctly described in this same conversation. Behavioral correction only: treat "we are now investigating something" as the trigger to create the file immediately, before the first diagnostic step, not after the first few - "already investigating in the chat" is not a substitute for the file existing.
