package com.dpfas.photobrowser.facerecognition

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FaceScanCacheTest {

    @Test
    fun `get returns null for a uri that was never scanned`() {
        val uri = Uri.parse("content://media/external/images/media/999")

        assertNull(FaceScanCache.get(uri))
    }

    @Test
    fun `put then get round-trips the faces for that uri`() {
        val uri = Uri.parse("content://media/external/images/media/1")
        val faces = listOf(ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.5f, 0.5f), floatArrayOf(1f, 2f)))

        FaceScanCache.put(uri, faces)

        assertEquals(faces, FaceScanCache.get(uri))
    }

    @Test
    fun `a scanned photo with zero faces is distinguishable from an unscanned one`() {
        val uri = Uri.parse("content://media/external/images/media/2")

        FaceScanCache.put(uri, emptyList())

        assertEquals(emptyList<ScannedFace>(), FaceScanCache.get(uri))
    }

    @Test
    fun `snapshot returns every scanned photo's faces`() {
        val uri1 = Uri.parse("content://media/external/images/media/3")
        val uri2 = Uri.parse("content://media/external/images/media/4")
        val face1 = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(1f))
        val face2 = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(2f))
        FaceScanCache.put(uri1, listOf(face1))
        FaceScanCache.put(uri2, listOf(face2))

        val snapshot = FaceScanCache.snapshot()

        assertEquals(listOf(face1), snapshot[uri1])
        assertEquals(listOf(face2), snapshot[uri2])
    }
}
