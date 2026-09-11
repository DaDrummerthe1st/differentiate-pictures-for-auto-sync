package com.dpfas.photobrowser.facerecognition

import android.net.Uri
import java.util.concurrent.ConcurrentHashMap

/**
 * In-memory, process-lifetime cache of the last face scan's results per photo, so the fullscreen
 * viewer can draw boxes (and the similar-faces search can compare embeddings) without re-running
 * detection. No persistence (no Room DB exists on-device yet, see documentation/mobile/TODO.md) -
 * lost on process death, rebuilt by the next scan.
 */
object FaceScanCache {
    private val facesByUri = ConcurrentHashMap<Uri, List<ScannedFace>>()

    fun put(uri: Uri, faces: List<ScannedFace>) {
        facesByUri[uri] = faces
    }

    /** Null means "not scanned yet" (distinct from a scanned photo with zero faces). */
    fun get(uri: Uri): List<ScannedFace>? = facesByUri[uri]

    /** A point-in-time copy of every scanned photo's faces, for a similarity search over the whole gallery. */
    fun snapshot(): Map<Uri, List<ScannedFace>> = facesByUri.toMap()

    /** Empties the cache - since this is a process-lifetime singleton, tests need this to isolate from each other. */
    fun clear() = facesByUri.clear()
}
