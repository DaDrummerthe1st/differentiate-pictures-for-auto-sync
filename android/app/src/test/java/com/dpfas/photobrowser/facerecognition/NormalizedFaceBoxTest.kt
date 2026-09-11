package com.dpfas.photobrowser.facerecognition

import org.junit.Assert.assertEquals
import org.junit.Test

class NormalizedFaceBoxTest {

    @Test
    fun `normalizedIn expresses a pixel box as fractions of the image size`() {
        val box = FaceBox(left = 50f, top = 100f, width = 200f, height = 50f, score = 0.9f, landmarks = emptyList())

        val normalized = box.normalizedIn(imageWidth = 1000, imageHeight = 500)

        assertEquals(0.05f, normalized.left, 1e-6f)
        assertEquals(0.2f, normalized.top, 1e-6f)
        assertEquals(0.25f, normalized.right, 1e-6f)
        assertEquals(0.3f, normalized.bottom, 1e-6f)
    }
}
