package com.dpfas.photobrowser

import android.net.Uri
import android.view.View
import android.widget.FrameLayout
import androidx.test.core.app.ApplicationProvider
import com.dpfas.photobrowser.facerecognition.FaceScanCache
import com.dpfas.photobrowser.facerecognition.NormalizedFaceBox
import com.dpfas.photobrowser.facerecognition.ScannedFace
import org.junit.Assert.assertEquals
import org.junit.Assert.assertSame
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
        val adapter = FullscreenPhotoPagerAdapter(uris, loadImage = { _, _ -> })

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

    @Test
    fun `onBindViewHolder loads that photo's cached faces into the overlay`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val faces = listOf(ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.4f, 0.4f), floatArrayOf(1f, 2f)))
        FaceScanCache.put(uris[0], faces)
        val adapter = FullscreenPhotoPagerAdapter(uris, loadImage = { _, _ -> })
        val parent = FrameLayout(context)

        val holder = adapter.onCreateViewHolder(parent, 0)
        adapter.onBindViewHolder(holder, 0)

        assertEquals(faces, holder.overlay.faces)
    }

    @Test
    fun `onBindViewHolder shows no faces for a photo that has not been scanned yet`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val adapter = FullscreenPhotoPagerAdapter(uris, loadImage = { _, _ -> })
        val parent = FrameLayout(context)

        val holder = adapter.onCreateViewHolder(parent, 0)
        adapter.onBindViewHolder(holder, 1)

        assertEquals(emptyList<ScannedFace>(), holder.overlay.faces)
    }

    @Test
    fun `the overlay is hidden unless showFaceBoxes is turned on`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        FaceScanCache.put(uris[0], listOf(ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.4f, 0.4f), floatArrayOf(1f))))
        val adapter = FullscreenPhotoPagerAdapter(uris, loadImage = { _, _ -> })
        val parent = FrameLayout(context)
        val holder = adapter.onCreateViewHolder(parent, 0)

        adapter.onBindViewHolder(holder, 0)
        assertEquals(View.GONE, holder.overlay.visibility)

        adapter.showFaceBoxes = true
        adapter.onBindViewHolder(holder, 0)
        assertEquals(View.VISIBLE, holder.overlay.visibility)
    }

    @Test
    fun `tapping a face in the overlay invokes onFaceTapped with that face`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val face = ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.4f, 0.4f), floatArrayOf(1f))
        FaceScanCache.put(uris[0], listOf(face))
        var tapped: ScannedFace? = null
        val adapter = FullscreenPhotoPagerAdapter(uris, loadImage = { _, _ -> }, onFaceTapped = { tapped = it })
        val parent = FrameLayout(context)
        val holder = adapter.onCreateViewHolder(parent, 0)

        adapter.onBindViewHolder(holder, 0)
        holder.overlay.onFaceTapped?.invoke(face)

        assertSame(face, tapped)
    }
}
