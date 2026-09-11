package com.dpfas.photobrowser.facerecognition

import android.graphics.Bitmap
import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.ByteArrayOutputStream
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class PhotoBitmapLoaderTest {

    private fun writeTempPng(width: Int, height: Int): Uri {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val bytes = ByteArrayOutputStream().use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
            out.toByteArray()
        }
        val file = File.createTempFile("photo_bitmap_loader_test", ".png")
        file.writeBytes(bytes)
        file.deleteOnExit()
        return Uri.fromFile(file)
    }

    // Regression test for the exact elvis-operator bug this function shipped with: decodeStream
    // always returns null in bounds-only mode, so a naive `... ?: return null` after that call
    // treats every successful decode as a failure. See PhotoBitmapLoader.kt's inline comment.
    @Test
    fun `load returns a real bitmap for a decodable image instead of always bailing out`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val uri = writeTempPng(100, 80)

        val bitmap = PhotoBitmapLoader.load(context, uri)

        assertNotNull(bitmap)
        assertEquals(100, bitmap!!.width)
        assertEquals(80, bitmap.height)
    }

    @Test
    fun `load returns null for a uri that cannot be opened`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val uri = Uri.fromFile(File("/no/such/file/here.png"))

        val bitmap = PhotoBitmapLoader.load(context, uri)

        assertNull(bitmap)
    }
}
