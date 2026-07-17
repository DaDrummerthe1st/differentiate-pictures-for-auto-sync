# Faster/leaner thumbnail generation

Status: **candidate, not evaluated or built**. Ties to
[2026-07-17-thumbnail-oom-under-load.md](2026-07-17-thumbnail-oom-under-load.md)
and [2026-07-17-pre-compile-thumbnails-ahead-of-time.md](2026-07-17-pre-compile-thumbnails-ahead-of-time.md).

## What

Raised 2026-07-17. Two candidate optimizations for the thumbnail
generation path, beyond what's already applied (the concurrency
semaphore and `Image.draft()`):

- **`pyvips`** as a future alternative to Pillow - a streaming image
  library, generally much lower peak memory for exactly this "shrink a
  big photo to a small thumbnail" workload, which matters on Pi-class
  hardware (see POLICY.md's resource-efficiency rule).

Neither evaluated or built - candidate follow-ups once the semaphore +
`Image.draft()` fixes are confirmed sufficient on their own, or once the
pre-compile work makes on-demand generation speed less critical.
