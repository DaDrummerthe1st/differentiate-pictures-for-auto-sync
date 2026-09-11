package com.dpfas.photobrowser.facerecognition

import android.graphics.Bitmap
import android.net.Uri

/**
 * Runs face detection+embedding over a list of photos, one at a time. No UI/identity-matching yet
 * (see documentation/mobile/TODO.md) - this exists purely to prove the pipeline works end to end,
 * reported via [onPhotoScanned] (Logcat in production, see MainActivity).
 */
class FaceScanRunner(
    private val loadBitmap: (Uri) -> Bitmap?,
    private val scan: (Bitmap) -> List<FaceResult>,
    private val onPhotoScanned: (uri: Uri, index: Int, total: Int, imageWidth: Int, imageHeight: Int, results: List<FaceResult>) -> Unit =
        { _, _, _, _, _, _ -> },
) {
    /** Returns the total number of faces found across all photos. */
    fun scanAll(uris: List<Uri>): Int {
        var totalFaces = 0
        uris.forEachIndexed { index, uri ->
            val bitmap = loadBitmap(uri)
            val results = if (bitmap != null) scan(bitmap) else emptyList()
            totalFaces += results.size
            onPhotoScanned(uri, index, uris.size, bitmap?.width ?: 0, bitmap?.height ?: 0, results)
        }
        return totalFaces
    }
}
