package com.dpfas.photobrowser.facerecognition

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FaceSimilarityTest {

    @Test
    fun `cosineSimilarity is 1 for identical vectors and 0 for orthogonal ones`() {
        val a = floatArrayOf(1f, 0f, 0f)
        val b = floatArrayOf(0f, 1f, 0f)

        assertEquals(1f, FaceSimilarity.cosineSimilarity(a, a), 1e-6f)
        assertEquals(0f, FaceSimilarity.cosineSimilarity(a, b), 1e-6f)
    }

    @Test
    fun `findSimilar ranks candidates by descending similarity to the query`() {
        val query = floatArrayOf(1f, 0f)
        val uri1 = Uri.parse("content://media/external/images/media/1")
        val uri2 = Uri.parse("content://media/external/images/media/2")
        val closeMatch = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(0.9f, 0.1f))
        val farMatch = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(0f, 1f))
        val candidates = mapOf(uri1 to listOf(farMatch), uri2 to listOf(closeMatch))

        val results = FaceSimilarity.findSimilar(query, candidates)

        assertEquals(listOf(uri2, uri1), results.map { it.uri })
    }

    @Test
    fun `findSimilar excludes the queried face itself by reference`() {
        val query = floatArrayOf(1f, 0f)
        val uri = Uri.parse("content://media/external/images/media/1")
        val self = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(1f, 0f))
        val other = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(0.5f, 0.5f))
        val candidates = mapOf(uri to listOf(self, other))

        val results = FaceSimilarity.findSimilar(query, candidates, excludeSelf = self)

        assertEquals(1, results.size)
        assertFalse(results.any { it.face === self })
    }

    @Test
    fun `findSimilar caps results at topK`() {
        val query = floatArrayOf(1f, 0f)
        val uri = Uri.parse("content://media/external/images/media/1")
        val faces = (0 until 10).map { ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(1f, it * 0.01f)) }

        val results = FaceSimilarity.findSimilar(query, mapOf(uri to faces), topK = 3)

        assertEquals(3, results.size)
    }
}
