package com.dpfas.photobrowser

import android.net.Uri
import android.widget.FrameLayout
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FullscreenPhotoPagerAdapterTest {

    private val uris = listOf(
        Uri.parse("content://media/external/images/media/1"),
        Uri.parse("content://media/external/images/media/2"),
    )

    @Test
    fun `getItemCount reflects the number of photos`() {
        val adapter = FullscreenPhotoPagerAdapter(uris) { _, _ -> }

        assertEquals(2, adapter.itemCount)
    }

    @Test
    fun `onBindViewHolder requests the uri for that position`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val requested = mutableListOf<Uri>()
        val adapter = FullscreenPhotoPagerAdapter(uris, loadImage = { _, uri -> requested.add(uri) })
        val parent = FrameLayout(context)

        val holder = adapter.onCreateViewHolder(parent, 0)
        adapter.onBindViewHolder(holder, 0)
        adapter.onBindViewHolder(holder, 1)

        assertEquals(uris, requested)
    }
}
