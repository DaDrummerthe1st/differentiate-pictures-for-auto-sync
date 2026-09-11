package com.dpfas.photobrowser.facerecognition

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class YuNetDecoderTest {

    @Test
    fun `decodeLevel skips cells below the score threshold`() {
        // cols=2, rows=1: cell 0 scores 1.0 (kept), cell 1 scores 0.0 (dropped).
        val cls = floatArrayOf(1f, 0f)
        val obj = floatArrayOf(1f, 1f)
        val bbox = FloatArray(2 * 4)
        val kps = FloatArray(2 * 10)

        val boxes = YuNetDecoder.decodeLevel(
            stride = 8, cols = 2, rows = 1,
            cls = cls, obj = obj, bbox = bbox, kps = kps,
            scoreThreshold = 0.5f,
        )

        assertEquals(1, boxes.size)
        assertEquals(1f, boxes[0].score, 1e-6f)
    }

    @Test
    fun `decodeLevel converts cell-relative regression targets into pixel-space box and landmarks`() {
        // Single cell (c=0, r=0), stride=8: tx=ty=0.5 centers the box at (4,4); tw=th=0 (exp(0)=1) gives an 8x8 box.
        val cls = floatArrayOf(1f)
        val obj = floatArrayOf(1f)
        val bbox = floatArrayOf(0.5f, 0.5f, 0f, 0f)
        val kps = FloatArray(10) { 0.5f }

        val boxes = YuNetDecoder.decodeLevel(
            stride = 8, cols = 1, rows = 1,
            cls = cls, obj = obj, bbox = bbox, kps = kps,
            scoreThreshold = 0.1f,
        )

        assertEquals(1, boxes.size)
        val box = boxes[0]
        assertEquals(0f, box.left, 1e-4f)
        assertEquals(0f, box.top, 1e-4f)
        assertEquals(8f, box.width, 1e-4f)
        assertEquals(8f, box.height, 1e-4f)
        assertEquals(5, box.landmarks.size)
        box.landmarks.forEach {
            assertEquals(4f, it.x, 1e-4f)
            assertEquals(4f, it.y, 1e-4f)
        }
    }

    @Test
    fun `decodeLevel indexes cells row-major so column offset shifts the decoded box`() {
        // cols=2, rows=1: cell at c=1 should decode to a box shifted right by one stride's worth of cell-center offset.
        val cls = floatArrayOf(0f, 1f)
        val obj = floatArrayOf(1f, 1f)
        val bbox = floatArrayOf(0f, 0f, 0f, 0f, 0.5f, 0.5f, 0f, 0f)
        val kps = FloatArray(2 * 10)

        val boxes = YuNetDecoder.decodeLevel(
            stride = 8, cols = 2, rows = 1,
            cls = cls, obj = obj, bbox = bbox, kps = kps,
            scoreThreshold = 0.1f,
        )

        assertEquals(1, boxes.size)
        // c=1: cx = (1 + 0.5) * 8 = 12, w = 8 -> left = 12 - 4 = 8
        assertEquals(8f, boxes[0].left, 1e-4f)
    }

    @Test
    fun `nms drops the lower-scoring box when two boxes overlap heavily`() {
        val a = FaceBox(left = 0f, top = 0f, width = 10f, height = 10f, score = 0.9f, landmarks = emptyList())
        val b = FaceBox(left = 1f, top = 1f, width = 10f, height = 10f, score = 0.5f, landmarks = emptyList())

        val kept = YuNetDecoder.nms(listOf(a, b), iouThreshold = 0.3f, topK = 50)

        assertEquals(1, kept.size)
        assertEquals(0.9f, kept[0].score, 1e-6f)
    }

    @Test
    fun `nms keeps both boxes when they do not overlap`() {
        val a = FaceBox(left = 0f, top = 0f, width = 10f, height = 10f, score = 0.9f, landmarks = emptyList())
        val b = FaceBox(left = 100f, top = 100f, width = 10f, height = 10f, score = 0.8f, landmarks = emptyList())

        val kept = YuNetDecoder.nms(listOf(a, b), iouThreshold = 0.3f, topK = 50)

        assertEquals(2, kept.size)
    }

    @Test
    fun `nms respects topK even when nothing overlaps`() {
        val boxes = (0 until 5).map {
            FaceBox(left = it * 100f, top = 0f, width = 10f, height = 10f, score = 1f - it * 0.01f, landmarks = emptyList())
        }

        val kept = YuNetDecoder.nms(boxes, iouThreshold = 0.3f, topK = 2)

        assertEquals(2, kept.size)
        assertTrue(kept[0].score >= kept[1].score)
    }
}
