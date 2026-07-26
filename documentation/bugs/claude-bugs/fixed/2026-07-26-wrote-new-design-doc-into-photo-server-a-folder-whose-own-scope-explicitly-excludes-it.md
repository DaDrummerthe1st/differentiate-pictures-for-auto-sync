# Wrote new design doc into photo-server, a folder whose own scope explicitly excludes it

See [README.md](../README.md) for what belongs here.

Status: fixed same session — see "What changed".

## What happened

Initially wrote the whole upload/sharing design as `documentation/photo-server/UPLOAD_AND_SHARE.md`, inside the `photo-server/` topic folder. That folder's own [README.md](../../../photo-server/README.md), read minutes earlier in the same session, already stated: "Nothing here should grow toward distributed storage, cross-household sharing, or AI-driven curation suggestions without an explicit decision to do so; those are separate, not-yet-scheduled pillars, not this folder's job." I placed the new content there anyway, without cross-checking the placement against that line.

## Why it happened

I'd read `photo-server/README.md`, `MOCKUP.md`, `TODO.md`, `DEFERRED.md`, and `DATA_DICTIONARY.md` before writing, specifically to match this project's documentation conventions/style — but used that reading pass only for style, not to check whether the new content's *scope* actually belonged in that folder at all. Likely cause: defaulted to "the biggest, most active existing topic folder for related work" rather than pausing to ask whether this new, vision-level, multi-user feature deserved its own topic folder — even though this project already has exactly that precedent (`distributed-sync/` exists as a separate topic from `photo-server/` for the same reason: future/vision scope that isn't "this folder's job").

## What changed

Joakim caught it mid-session ("all the documentation should be placed in folders that are logic... perhaps documentation/upload and documentation/share"). Resolved via [AskUserQuestion], confirming a single new topic folder `documentation/upload-and-share/` (matching the branch name and this project's one-topic-per-subject convention) over either leaving it in `photo-server/` or splitting it into two folders that would have forced the shared ownership/moderation model to live in one and be cross-referenced from the other. Moved the content there (`README.md`, `TODO.md`, `OWNERSHIP.md`, `UPLOAD.md`, `SHARING.md`, `EVENTS.md`) and fixed every cross-reference in `DATA_DICTIONARY.md`, `VISION.md`, `POLICY.md`, `DEFERRED.md`, the top-level `README.md`, and `photo-server/TODO.md`.

**Going forward**: before writing a new substantial doc, explicitly check the target folder's own README.md for an out-of-scope statement covering this kind of content — don't rely on having read it once earlier in the session for a different purpose.
