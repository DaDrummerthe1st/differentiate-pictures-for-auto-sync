# Fix repeated elvis-operator bounds-decode bug, add WORKFLOW.md prevention rule

New on-device face-scan code (`PhotoBitmapLoader`'s bounds-only decode) repeated the already-fixed
2026-09-06 photo-grid elvis-operator bug shape (`decodeStream` always returns `null` in
bounds-only mode, so `?: return null` right after it treats every success as a failure), despite
the original bug file having been read earlier in the same session. Bug file already landed via a
concurrent peer session's commit (746ef9f); this entry adds the WORKFLOW.md debugging-discipline
rule requiring a `documentation/bugs/` grep for this exact pattern before writing another
bounds-only decode.

- **Doc size**: `documentation/policies/WORKFLOW.md` +817 chars.
