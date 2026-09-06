package com.dpfas.photobrowser

import android.content.Context
import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import androidx.viewpager2.widget.ViewPager2
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class FullscreenPhotoActivityTest {

    private val uris = listOf(
        Uri.parse("content://media/external/images/media/1"),
        Uri.parse("content://media/external/images/media/2"),
        Uri.parse("content://media/external/images/media/3"),
    )

    @Test
    fun `createIntent carries the photo uris and start position`() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val intent = FullscreenPhotoActivity.createIntent(context, uris, startPosition = 2)

        assertEquals(
            uris,
            intent.getParcelableArrayListExtra(FullscreenPhotoActivity.EXTRA_PHOTO_URIS, Uri::class.java),
        )
        assertEquals(2, intent.getIntExtra(FullscreenPhotoActivity.EXTRA_START_POSITION, -1))
    }

    @Test
    fun `onCreate wires the pager to the full photo list starting at the tapped position`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = FullscreenPhotoActivity.createIntent(context, uris, startPosition = 2)

        val controller = Robolectric.buildActivity(FullscreenPhotoActivity::class.java, intent)
        controller.create()

        val pager = controller.get().findViewById<ViewPager2>(R.id.fullscreen_pager)
        assertEquals(3, pager.adapter?.itemCount)
        assertEquals(2, pager.currentItem)
    }

    @Test
    fun `onCreate wires the injected loadImage into the pager adapter`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = FullscreenPhotoActivity.createIntent(context, uris, startPosition = 0)
        val requested = mutableListOf<Uri>()

        val controller = Robolectric.buildActivity(FullscreenPhotoActivity::class.java, intent)
        controller.get().loadImage = { _, uri -> requested.add(uri) }
        controller.create()

        val pager = controller.get().findViewById<ViewPager2>(R.id.fullscreen_pager)
        val adapter = pager.adapter as FullscreenPhotoPagerAdapter
        val holder = adapter.onCreateViewHolder(pager, 0)
        adapter.onBindViewHolder(holder, 0)

        assertEquals(listOf(uris[0]), requested)
    }
}
