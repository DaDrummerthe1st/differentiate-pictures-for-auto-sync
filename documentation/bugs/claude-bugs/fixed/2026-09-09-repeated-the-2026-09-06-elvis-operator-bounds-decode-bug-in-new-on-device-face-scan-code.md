# Repeated the 2026-09-06 elvis-operator bounds-decode bug in new on-device face-scan code

See [README.md](../README.md) for what belongs here.

## What happened

Building the on-device face-recognition pipeline, I wrote `PhotoBitmapLoader.load()`'s bounds-probe
decode as:

```kotlin
resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) } ?: return null
```

`BitmapFactory.decodeStream` always returns `null` in bounds-only mode (`inJustDecodeBounds =
true`) - that's how bounds probing works, it never allocates a bitmap. So the `?: return null`
fired on *every* call, success or failure, and the function bailed out before real decoding ever
ran. The face scanner then processed all 107 test photos in ~1.6 seconds, logged "0 faces" for
every single one, threw no exception, and even showed a normal-looking summary Toast - Joakim
caught it only because he could see real faces in the photo grid ("0 faces is inaccurate, there
are a lot of faces there"). This is the exact same shape as
[../fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md](../fixed/2026-09-06-photo-grid-always-blank-bounds-decode-null-trips-elvis-always-returns-null-thumbnail-SOLVED.md) -
same file even referenced in `documentation/mobile/README.md`'s Status section, which I had read
earlier in this same session before writing the new decode code.

## Why it happened

I wrote a new `BitmapFactory` bounds-probe decode from general Android knowledge without checking
whether this exact area (bounds-only decode + elvis operator) already had a documented failure
mode in this repo, even though I'd read the file describing exactly that failure a few turns
earlier for unrelated context (understanding the mobile app's history). Nothing prompted a "have I
seen this shape before" check at the point I actually wrote the vulnerable line - the connection
between "I'm about to write a `BitmapFactory` bounds-decode call" and "there's a fixed bug about
that exact pattern in this repo" was never made.

## What changed

Added a rule to [WORKFLOW.md](../../../policies/WORKFLOW.md)'s Debugging discipline section:
before writing a `BitmapFactory` bounds-only decode (`inJustDecodeBounds = true`) or any other code
whose success signal isn't the call's own return value, check `documentation/bugs/` (`grep -ri` for
the relevant API/pattern) for a prior incident in the same shape - this repo has hit the
elvis-after-bounds-only-decode trap twice now. Also added an inline code comment at the fix site
(`PhotoBitmapLoader.kt`) naming the exact same trap, and a regression test
(`PhotoBitmapLoaderTest.kt`) asserting a real decodable image actually round-trips through `load()`
instead of always returning null.
