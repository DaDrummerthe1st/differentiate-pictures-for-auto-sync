package com.dpfas.photobrowser.facerecognition

import org.junit.Assert.assertEquals
import org.junit.Test

class CropRectTest {

    @Test
    fun `adds the margin ratio on every side when there is room`() {
        val rect = marginedCropRect(left = 100f, top = 100f, right = 200f, bottom = 150f, marginRatio = 0.2f, imageWidth = 1000, imageHeight = 1000)

        // width=100 -> marginX=20, height=50 -> marginY=10
        assertEquals(80, rect.x)
        assertEquals(90, rect.y)
        assertEquals(140, rect.width)
        assertEquals(70, rect.height)
    }

    @Test
    fun `clamps to the image bounds when the margin would extend past an edge`() {
        val rect = marginedCropRect(left = 0f, top = 0f, right = 40f, bottom = 40f, marginRatio = 0.5f, imageWidth = 200, imageHeight = 200)

        assertEquals(0, rect.x)
        assertEquals(0, rect.y)
        assertEquals(60, rect.width)
        assertEquals(60, rect.height)
    }

    @Test
    fun `never returns a zero or negative size`() {
        val rect = marginedCropRect(left = 50f, top = 50f, right = 50f, bottom = 50f, marginRatio = 0f, imageWidth = 100, imageHeight = 100)

        assertEquals(1, rect.width)
        assertEquals(1, rect.height)
    }
}
