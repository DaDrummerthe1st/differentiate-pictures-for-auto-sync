# Photo grid always blank: bounds-decode null trips elvis, always returns null thumbnail

Status: **fixed**. Keep this file as the full chronological trail as more is learned - don't overwrite conclusions.

## Symptom

First real run of `android/`'s photo-browser app (see [mobile/README.md](../../../mobile/README.md))
after getting the Gradle wrapper/toolchain working: the app builds, installs, requests and gets the
`READ_MEDIA_IMAGES` permission, and its `GridView` lays out the correct number of cells matching
MediaStore's actual photo count - but every cell renders pure white. `adb screencap` confirmed exact
solid-white pixels (255,255,255) in every cell across multiple retries and wait times, ruling out an
async-decode timing issue. `content read` on the same MediaStore URIs from the shell returned the
full, correct byte count, ruling out a data/permission problem.

## Investigation log

1. Confirmed MediaStore itself had the pushed test photos indexed correctly (`content query`,
   correct `_size` matching the real files, `content read` returning full byte counts).
2. Confirmed the app's own `READ_MEDIA_IMAGES` runtime permission was granted (`dumpsys package`).
3. Confirmed via `uiautomator dump` that `PhotoAdapter.getView()` was being called correctly and
   laying out the right number of `ImageView` cells with correct bounds - so the MediaStore query
   and grid population were working. Only the actual bitmap rendering was failing, silently, with
   zero exceptions anywhere in logcat.
4. Added temporary `Log.d`/`Log.e` instrumentation directly in `PhotoAdapter.decodeSampledThumbnail`
   and the executor block in `getView`. This showed `decodeSampledThumbnail` returning `null` for
   **every single image**, with no exception ever thrown - a silent, always-null failure.
5. Added one more log line probing `bounds.outWidth`/`outHeight` right after the first
   (bounds-only) `BitmapFactory.decodeStream` call. That log line **never printed** - execution
   never reached it, meaning the function was returning early, before even getting to compute
   `inSampleSize`.

## Root cause (confirmed)

```kotlin
resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) }
    ?: return null
```

`BitmapFactory.decodeStream` is documented to return `null` when `inJustDecodeBounds = true` in its
`Options` - that's the whole point of a bounds-only probe, it only has the side effect of populating
`bounds.outWidth`/`outHeight`/`outMimeType`, its actual return value is deliberately `null`. But that
`null` becomes the return value of the `.use { }` block, which becomes the value of
`resolver.openInputStream(uri)?.use { ... }` as a whole - and the `?: return null` elvis operator
was written to guard against `openInputStream` itself returning `null` (stream unavailable), but it
can't distinguish that from "the stream opened fine, but the intentionally-null bounds-probe result
propagated through". The result: this line unconditionally returns `null` from
`decodeSampledThumbnail` for every valid image, every time, before the real thumbnail decode ever
runs. This bug has existed since the function was first written and was never caught because the
app had never actually been built/run before this session - see mobile/README.md's "not yet
verified to actually build or run" note.

## Fix

Split the null-stream-check from the decode-call's return value:

```kotlin
val boundsStream = resolver.openInputStream(uri) ?: return null
boundsStream.use { BitmapFactory.decodeStream(it, null, bounds) }
```

Now the early return only fires when the stream genuinely can't be opened; the (deliberately null)
result of the bounds-only decode call is discarded rather than propagated. Fixed in
`android/app/src/main/java/com/dpfas/photobrowser/PhotoAdapter.kt`, confirmed working by installing
on the `Motorola_Moto_G54_5G` AVD with real test photos from `resources/test_pictures/` and
visually confirming thumbnails render.

## Related, separate issue hit during the same session (not a code bug)

After fixing the above, the grid kept showing exactly 15 photos regardless of how many more were
pushed to the device (21, then all 107) and regardless of re-granting permissions, `pm clear`,
uninstall/reinstall, or even a full emulator reboot. Root cause never fully pinned down with
certainty, but strongly pointed to Android 14+'s "Selected photos" limited-access grant (a separate
mechanism from the regular `READ_MEDIA_IMAGES` runtime permission, keyed by an internal MediaProvider
grant list that doesn't auto-expand when new photos are added) most likely triggered by an early
blind `adb shell input tap` sent while testing the permission-denied path. Resolved by: uninstalling
the app, rebooting the emulator, reinstalling, and granting `READ_MEDIA_IMAGES` via `pm grant` before
ever launching the Activity for the first time (so the picker/partial-access flow never triggers).
No code change was needed for this part - flagging it here since it cost significant debugging time
and the exact trigger/fix mechanism isn't 100% certain, in case it recurs.
