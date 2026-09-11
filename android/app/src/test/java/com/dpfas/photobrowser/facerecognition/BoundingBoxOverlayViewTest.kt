package com.dpfas.photobrowser.facerecognition

import android.graphics.Matrix
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertSame
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class BoundingBoxOverlayViewTest {

    @Test
    fun `boxToViewRect converts a normalized box to image-space pixels under the identity matrix`() {
        val box = NormalizedFaceBox(left = 0.1f, top = 0.2f, right = 0.5f, bottom = 0.6f)

        val rect = BoundingBoxOverlayView.boxToViewRect(box, imageWidth = 1000, imageHeight = 500, matrix = Matrix())

        assertEquals(100f, rect.left, 1e-3f)
        assertEquals(100f, rect.top, 1e-3f)
        assertEquals(500f, rect.right, 1e-3f)
        assertEquals(300f, rect.bottom, 1e-3f)
    }

    @Test
    fun `boxToViewRect applies the display matrix so a zoomed-in view scales boxes with it`() {
        val box = NormalizedFaceBox(left = 0.1f, top = 0.1f, right = 0.2f, bottom = 0.2f)
        val zoomedIn2x = Matrix().apply { setScale(2f, 2f) }

        val rect = BoundingBoxOverlayView.boxToViewRect(box, imageWidth = 100, imageHeight = 100, matrix = zoomedIn2x)

        // Image-space rect is (10,10)-(20,20); 2x scale doubles it.
        assertEquals(20f, rect.left, 1e-3f)
        assertEquals(20f, rect.top, 1e-3f)
        assertEquals(40f, rect.right, 1e-3f)
        assertEquals(40f, rect.bottom, 1e-3f)
    }

    @Test
    fun `findTappedFace returns the face whose box contains the tapped point`() {
        val face = ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.5f, 0.5f), floatArrayOf(1f))

        val tapped = BoundingBoxOverlayView.findTappedFace(
            listOf(face), x = 200f, y = 200f, imageWidth = 1000, imageHeight = 1000, matrix = Matrix(),
        )

        assertSame(face, tapped)
    }

    @Test
    fun `findTappedFace returns null when the point falls outside every box`() {
        val face = ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.2f, 0.2f), floatArrayOf(1f))

        val tapped = BoundingBoxOverlayView.findTappedFace(
            listOf(face), x = 900f, y = 900f, imageWidth = 1000, imageHeight = 1000, matrix = Matrix(),
        )

        assertNull(tapped)
    }
}
