# File bug report: uploads report finished but nothing lands

Joakim reported that after testing the just-deployed upload-progress fix live, uploads appeared to finish with no persistent visible error, but no files landed in `dpfas_media/<username>/` or appeared in the browser. No live repro yet (reported at session close) - filed with a ranked hypothesis list from static code reading, leading candidate being `/api/upload`'s `PICTURE_EXTS` allowlist (missing `.heic`, notably) or its 25MB size cap silently 400ing and the existing one-shot `alert()` failure message going unnoticed.

- **Doc size**: bug file 0 → 5,616 characters (new).
