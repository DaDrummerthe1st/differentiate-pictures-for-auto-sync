# Design audience circles as reusable share-target tags, resolve preference-aggregate dependency

Joakim asked whether "groups" (the audience-scope primitive flagged missing last session) could be tags too, and whether a group could be one person. Yes to both: a circle is a tag whose `tag_references` list member entities, reusing the exact mechanism relationships/story/co-presence already share rather than a new table. A one-member circle is the unremarkable base case, not a special path — sharing always expands a circle's members through the existing per-recipient grant mechanics.

Real schema note surfaced, not glossed over: a circle tag isn't about any one photo, so `tags.photo_id` (currently `NOT NULL`, part of the live `unique(photo_id, user_id, tag)` constraint) needs relaxing — the story/narrative category already implicitly raises the same question, flagged to resolve both together. Also flagged a naming collision: the existing "Co-presence/group" category already uses "group" for a different thing (who's depicted together, not who to share with) — "circle" proposed to keep them apart, not decided as final.

SHARING.md gets a fourth share entry point (pick a saved circle, fans out through the existing username/email resolution). ARCHITECTURE.md's privacy-preference-aggregate note updated to point at this resolution instead of describing an open gap. GLOSSARY.md gets an "Audience circle" entry.

- **Doc size**: +4,230 chars (net, across TAXONOMY.md, ARCHITECTURE.md, SHARING.md, GLOSSARY.md; Unicode codepoints, per DOC_METRICS.md methodology).
