# Turn prototypes/mockup README into a stub, relocate unique content to tags/UX_FLOWS.md; fix dead-link-checker false positive on code-span examples

`prototypes/mockup/README.md` had drifted from a stub into restating real tag-taxonomy design content already covered in `tags/UX_FLOWS.md`/`TAXONOMY.md` — cut the restated parts and moved the one genuinely unique paragraph (the mockup's two illustrative schema simplifications) into a new UX_FLOWS.md section. Also found and fixed (TDD) a dead-link-checker false positive: markdown-link syntax written as an illustrative example inside backticks was being flagged as a real broken link.

- **Doc size**: prototypes/mockup/README.md 2,360 → 695; documentation/tags/UX_FLOWS.md 4,953 → 5,878. Combined: 7,313 → 6,573 chars (−740).
