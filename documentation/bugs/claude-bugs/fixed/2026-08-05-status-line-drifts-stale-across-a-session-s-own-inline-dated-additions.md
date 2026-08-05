# Status line drifts stale across a session's own inline dated additions

See [README.md](../README.md) for what belongs here.

## What happened

Joakim asked for an audit pass over this session's own doc edits (inconsistencies, space savings, easier hand-off for the next session). Re-reading [tags/TAXONOMY.md](../../../tags/TAXONOMY.md) and [curation/ARCHITECTURE.md](../../../curation/ARCHITECTURE.md) fresh turned up that both files' own `## Status` sections were stale relative to their bodies: TAXONOMY.md's Status line mentioned only the 2026-08-04 provenance addition, silently missing the same day's own later custom-privacy-categories and audience-circles sections; ARCHITECTURE.md's Status line still read "Designed 2026-08-02, theory only," not mentioning any of the several dated additions layered in on 2026-08-03/04/05 (usage-intent reweighting, the per-household identity classifier, the privacy-preference aggregate, cross-household linking). Each individual addition was itself well-dated and cross-referenced inline — the lapse was narrower: the file's own summary line at the bottom wasn't kept in sync with its own growing body, within the same session that grew it.

## Why it happened

Each addition this session was made as a self-contained edit (find the right section, insert dated content, move to the next request) without a habit of also touching that same file's `## Status` footer as part of the same edit. The existing "Keeping docs current" rule ([README.md](../../../README.md)) covers docs drifting from *code*, and CLAUDE.md's per-turn rule covers a *tagged term* going into GLOSSARY.md same-turn — neither explicitly named a file's own internal Status summary as something that also needs same-pass upkeep, so there was no standing rule actually being violated on paper, just a real gap the audit surfaced.

## What changed

Added an explicit line to [documentation/README.md](../../../README.md)'s "Keeping docs current" section: when adding a dated inline addition to a file's body, update that file's own `## Status` section in the same edit, not deferred to a later cleanup pass — closing the specific gap this lapse exposed. The two stale Status lines found this session were fixed as part of the same pass that filed this report (TAXONOMY.md, ARCHITECTURE.md), and DETECTORS.md's Status line was double-checked and brought current too since it's the third file heavily edited this session.
