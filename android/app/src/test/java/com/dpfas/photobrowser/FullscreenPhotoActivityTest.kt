package com.dpfas.photobrowser

import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FullscreenPhotoActivityTest {

    @Test
    fun `createIntent carries the photo uri`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val uri = Uri.parse("content://media/external/images/media/42")

        val intent = FullscreenPhotoActivity.createIntent(context, uri)

        assertEquals(uri, intent.getParcelableExtra(FullscreenPhotoActivity.EXTRA_PHOTO_URI, Uri::class.java))
    }

    @Test
    fun `onCreate loads the uri from the intent`() {
        val uri = Uri.parse("content://media/external/images/media/42")
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val intent = FullscreenPhotoActivity.createIntent(context, uri)
        val requested = mutableListOf<Uri>()

        val controller = Robolectric.buildActivity(FullscreenPhotoActivity::class.java, intent)
        controller.get().loadImage = { _, requestedUri -> requested.add(requestedUri) }
        controller.create()

        assertEquals(listOf(uri), requested)
    }
}
