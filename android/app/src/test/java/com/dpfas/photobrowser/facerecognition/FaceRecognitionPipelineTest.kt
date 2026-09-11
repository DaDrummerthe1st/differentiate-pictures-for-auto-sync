package com.dpfas.photobrowser.facerecognition

import android.graphics.Bitmap
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FaceRecognitionPipelineTest {

    private class FakeDetector(private val boxes: List<FaceBox>) : FaceDetector {
        var lastBitmap: Bitmap? = null
        override fun detect(bitmap: Bitmap): List<FaceBox> {
            lastBitmap = bitmap
            return boxes
        }
    }

    private class FakeEmbedder : FaceEmbedder {
        val crops = mutableListOf<Bitmap>()
        override fun embed(faceCrop: Bitmap): FloatArray {
            crops.add(faceCrop)
            return floatArrayOf(faceCrop.width.toFloat(), faceCrop.height.toFloat())
        }
    }

    @Test
    fun `scan with no detected faces never calls the embedder`() {
        val embedder = FakeEmbedder()
        val pipeline = FaceRecognitionPipeline(FakeDetector(emptyList()), embedder)
        val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)

        val results = pipeline.scan(bitmap)

        assertTrue(results.isEmpty())
        assertTrue(embedder.crops.isEmpty())
    }

    @Test
    fun `scan embeds a crop for each detected face and pairs it with that face's box`() {
        val box = FaceBox(left = 50f, top = 50f, width = 40f, height = 40f, score = 0.9f, landmarks = emptyList())
        val embedder = FakeEmbedder()
        val pipeline = FaceRecognitionPipeline(FakeDetector(listOf(box)), embedder)
        val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)

        val results = pipeline.scan(bitmap)

        assertEquals(1, results.size)
        assertEquals(box, results[0].box)
        assertEquals(1, embedder.crops.size)
        // 40x40 box + 20% margin each side (0.2*40=8) -> 56x56, within a 200x200 bitmap.
        assertEquals(56, embedder.crops[0].width)
        assertEquals(56, embedder.crops[0].height)
    }

    @Test
    fun `crop clamps to the bitmap bounds when the box margin would extend past an edge`() {
        // Box sits right at the top-left corner, so the margin has nowhere to go on that side.
        val box = FaceBox(left = 0f, top = 0f, width = 40f, height = 40f, score = 0.9f, landmarks = emptyList())
        val embedder = FakeEmbedder()
        val pipeline = FaceRecognitionPipeline(FakeDetector(listOf(box)), embedder)
        val bitmap = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)

        pipeline.scan(bitmap)

        val crop = embedder.crops[0]
        assertTrue("crop width ${crop.width} should not exceed box+margin on the open side", crop.width <= 48)
        assertTrue(crop.width > 0)
        assertTrue(crop.height > 0)
    }

    @Test
    fun `scan passes the original bitmap to the detector`() {
        val embedder = FakeEmbedder()
        val detector = FakeDetector(emptyList())
        val pipeline = FaceRecognitionPipeline(detector, embedder)
        val bitmap = Bitmap.createBitmap(64, 64, Bitmap.Config.ARGB_8888)

        pipeline.scan(bitmap)

        assertEquals(bitmap, detector.lastBitmap)
    }
}
