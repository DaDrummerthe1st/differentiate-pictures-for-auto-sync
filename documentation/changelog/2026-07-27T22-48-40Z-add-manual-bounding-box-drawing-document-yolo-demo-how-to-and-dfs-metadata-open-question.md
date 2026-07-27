# Add manual bounding-box drawing; document YOLO demo how-to and DFS metadata open question

Discussion surfaced three gaps: the tagging design only covered detector-sourced
boxes, with no way to draw one by hand; no documented path to actually see object
detection run on a real photo today; and no answer for where tag metadata lives
once a photo's bytes are scattered across the future distributed file system.
Closed the first two (design in `tags/UX_FLOWS.md` + a working click-drag
implementation in `prototypes/mockup/`; a how-to note in
`picture-handling/TODO.md`, not executed — Joakim wants it left for a later
session). Flagged the third as an open tension in `distributed-sync/TODO.md`,
same "named, not designed" treatment as `OWNERSHIP.md`'s existing unresolved
tensions — not answered, since nothing already decided covers it.

- **Doc size**: `tags/UX_FLOWS.md` 3789 → 5310 (+1521, manual-box design
  section). `picture-handling/TODO.md` 2429 → 4185 (+1756, YOLO how-to note).
  `distributed-sync/TODO.md` 1014 → 1850 (+836, DFS-metadata open question).
  `prototypes/mockup/README.md` 1862 → 2372 (+510).
