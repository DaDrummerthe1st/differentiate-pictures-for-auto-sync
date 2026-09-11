package com.dpfas.photobrowser.facerecognition

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FaceScanRunnerTest {

    private val uris = listOf(
        Uri.parse("content://media/external/images/media/1"),
        Uri.parse("content://media/external/images/media/2"),
        Uri.parse("content://media/external/images/media/3"),
    )

    @Test
    fun `scanAll sums face counts across all photos`() {
        var callIndex = 0
        val orderedCounts = listOf(2, 0, 1)
        val runner = FaceScanRunner(
            loadBitmap = { android.graphics.Bitmap.createBitmap(1, 1, android.graphics.Bitmap.Config.ARGB_8888) },
            scan = {
                val count = orderedCounts[callIndex]
                callIndex++
                List(count) { FaceResult(FaceBox(0f, 0f, 1f, 1f, 1f, emptyList()), floatArrayOf()) }
            },
        )

        val total = runner.scanAll(uris)

        assertEquals(3, total)
    }

    @Test
    fun `scanAll treats an undecodable photo as zero faces without calling scan`() {
        var scanCalls = 0
        val runner = FaceScanRunner(
            loadBitmap = { null },
            scan = { scanCalls++; emptyList() },
        )

        val total = runner.scanAll(uris)

        assertEquals(0, total)
        assertEquals(0, scanCalls)
    }

    @Test
    fun `scanAll reports progress for every photo with its own uri and face count`() {
        val orderedCounts = listOf(2, 0, 1)
        var callIndex = 0
        val progress = mutableListOf<Triple<Uri, Int, Int>>()
        val runner = FaceScanRunner(
            loadBitmap = { android.graphics.Bitmap.createBitmap(1, 1, android.graphics.Bitmap.Config.ARGB_8888) },
            scan = {
                val count = orderedCounts[callIndex]
                callIndex++
                List(count) { FaceResult(FaceBox(0f, 0f, 1f, 1f, 1f, emptyList()), floatArrayOf()) }
            },
            onPhotoScanned = { uri, index, total, _, _, results -> progress.add(Triple(uri, index, results.size)).also { assertEquals(3, total) } },
        )

        runner.scanAll(uris)

        assertEquals(listOf(Triple(uris[0], 0, 2), Triple(uris[1], 1, 0), Triple(uris[2], 2, 1)), progress)
    }

    @Test
    fun `scanAll reports the decoded bitmap's dimensions for a successfully loaded photo`() {
        val dimensions = mutableListOf<Pair<Int, Int>>()
        val runner = FaceScanRunner(
            loadBitmap = { android.graphics.Bitmap.createBitmap(64, 48, android.graphics.Bitmap.Config.ARGB_8888) },
            scan = { emptyList() },
            onPhotoScanned = { _, _, _, width, height, _ -> dimensions.add(width to height) },
        )

        runner.scanAll(uris)

        assertEquals(List(3) { 64 to 48 }, dimensions)
    }
}
