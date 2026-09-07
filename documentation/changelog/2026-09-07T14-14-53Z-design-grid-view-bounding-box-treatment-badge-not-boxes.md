# Design grid-view bounding-box treatment: badge not boxes

Joakim asked how the grid should surface detected bounding boxes once on-device object detection
exists. Researched Google Photos/Apple Photos precedent: neither draws box outlines in grid view —
both defer to a separate collection/grouping UI, using badges rather than drawn boxes on grid
tiles. Proposed the same for this app: no boxes in the grid, a small corner badge instead, with
actual box-level tap/confirm interaction staying in the fullscreen view per the design
tags/UX_FLOWS.md already has.

- **Doc size**: `mobile/UX_FLOWS.md` +1565 chars.
