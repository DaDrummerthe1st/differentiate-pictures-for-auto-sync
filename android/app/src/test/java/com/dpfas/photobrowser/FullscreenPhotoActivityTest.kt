package com.dpfas.photobrowser

import android.content.Context
import android.net.Uri
import android.widget.CheckBox
import androidx.test.core.app.ApplicationProvider
import androidx.viewpager2.widget.ViewPager2
import com.dpfas.photobrowser.facerecognition.NormalizedFaceBox
import com.dpfas.photobrowser.facerecognition.ScannedFace
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
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

    @Test
    fun `face boxes are off by default and the checkbox turns them on`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = FullscreenPhotoActivity.createIntent(context, uris, startPosition = 0)

        val controller = Robolectric.buildActivity(FullscreenPhotoActivity::class.java, intent)
        controller.create()

        val pager = controller.get().findViewById<ViewPager2>(R.id.fullscreen_pager)
        val adapter = pager.adapter as FullscreenPhotoPagerAdapter
        assertFalse(adapter.showFaceBoxes)

        controller.get().findViewById<CheckBox>(R.id.show_face_boxes_checkbox).isChecked = true

        assertTrue(adapter.showFaceBoxes)
    }

    @Test
    fun `onCreate wires the injected onFaceTapped into the pager adapter`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = FullscreenPhotoActivity.createIntent(context, uris, startPosition = 0)
        val tapped = mutableListOf<ScannedFace>()
        val face = ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.2f, 0.2f), floatArrayOf(1f))

        val controller = Robolectric.buildActivity(FullscreenPhotoActivity::class.java, intent)
        controller.get().onFaceTapped = { tapped.add(it) }
        controller.create()

        val pager = controller.get().findViewById<ViewPager2>(R.id.fullscreen_pager)
        val adapter = pager.adapter as FullscreenPhotoPagerAdapter
        val holder = adapter.onCreateViewHolder(pager, 0)
        adapter.onBindViewHolder(holder, 0)
        holder.overlay.onFaceTapped?.invoke(face)

        assertEquals(listOf(face), tapped)
    }

    @Test
    fun `the default onFaceTapped opens the similar-faces grid for that face's embedding`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = FullscreenPhotoActivity.createIntent(context, uris, startPosition = 0)
        val embedding = floatArrayOf(1f, 2f, 3f)

        val controller = Robolectric.buildActivity(FullscreenPhotoActivity::class.java, intent)
        controller.create()
        controller.get().onFaceTapped(ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), embedding))

        val started = shadowOf(controller.get()).nextStartedActivity
        assertEquals(SimilarFacesActivity::class.java.name, started.component?.className)
        assertArrayEquals(embedding, started.getFloatArrayExtra(SimilarFacesActivity.EXTRA_QUERY_EMBEDDING)!!, 0f)
    }
}
