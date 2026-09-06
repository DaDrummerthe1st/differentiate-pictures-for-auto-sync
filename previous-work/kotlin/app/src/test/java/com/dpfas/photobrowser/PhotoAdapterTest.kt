package com.dpfas.photobrowser

import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class PhotoAdapterTest {

    private val uris = listOf(
        Uri.parse("content://media/external/images/media/1"),
        Uri.parse("content://media/external/images/media/2"),
    )

    @Test
    fun `getView requests the uri for that position`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val requested = mutableListOf<Uri>()
        val adapter = PhotoAdapter(context, uris, loadImage = { _, uri -> requested.add(uri) })
        val parent = android.widget.GridView(context)

        adapter.getView(0, null, parent)
        adapter.getView(1, null, parent)

        assertEquals(uris, requested)
    }

    @Test
    fun `getView reuses the passed-in convertView instead of inflating a new one`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val adapter = PhotoAdapter(context, uris, loadImage = { _, _ -> })
        val parent = android.widget.GridView(context)

        val first = adapter.getView(0, null, parent)
        val second = adapter.getView(1, first, parent)

        assertEquals(first, second)
    }
}
