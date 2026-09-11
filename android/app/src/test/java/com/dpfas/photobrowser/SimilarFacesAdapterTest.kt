package com.dpfas.photobrowser

import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import com.dpfas.photobrowser.facerecognition.FaceMatch
import com.dpfas.photobrowser.facerecognition.NormalizedFaceBox
import com.dpfas.photobrowser.facerecognition.ScannedFace
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class SimilarFacesAdapterTest {

    private val matches = listOf(
        FaceMatch(
            Uri.parse("content://media/external/images/media/1"),
            ScannedFace(NormalizedFaceBox(0.1f, 0.1f, 0.4f, 0.4f), floatArrayOf(1f)),
            similarity = 0.9f,
        ),
        FaceMatch(
            Uri.parse("content://media/external/images/media/2"),
            ScannedFace(NormalizedFaceBox(0.2f, 0.2f, 0.5f, 0.5f), floatArrayOf(2f)),
            similarity = 0.8f,
        ),
    )

    @Test
    fun `getView requests the match for that position`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val requested = mutableListOf<FaceMatch>()
        val adapter = SimilarFacesAdapter(context, matches, loadImage = { _, match -> requested.add(match) })
        val parent = android.widget.GridView(context)

        adapter.getView(0, null, parent)
        adapter.getView(1, null, parent)

        assertEquals(matches, requested)
    }

    @Test
    fun `getCount reflects the number of matches`() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val adapter = SimilarFacesAdapter(context, matches) { _, _ -> }

        assertEquals(2, adapter.count)
    }
}
