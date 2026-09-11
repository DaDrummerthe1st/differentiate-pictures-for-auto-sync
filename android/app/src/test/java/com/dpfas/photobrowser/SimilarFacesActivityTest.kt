package com.dpfas.photobrowser

import android.content.Context
import android.net.Uri
import android.view.View
import android.widget.GridView
import android.widget.TextView
import androidx.test.core.app.ApplicationProvider
import com.dpfas.photobrowser.facerecognition.FaceMatch
import com.dpfas.photobrowser.facerecognition.FaceScanCache
import com.dpfas.photobrowser.facerecognition.NormalizedFaceBox
import com.dpfas.photobrowser.facerecognition.ScannedFace
import org.junit.Assert.assertEquals
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class SimilarFacesActivityTest {

    private val queryEmbedding = floatArrayOf(1f, 2f, 3f)
    private val queryBox = NormalizedFaceBox(0.1f, 0.1f, 0.2f, 0.2f)
    private val queryFace = ScannedFace(queryBox, queryEmbedding)

    @Test
    fun `createIntent carries the tapped face's embedding and box`() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val intent = SimilarFacesActivity.createIntent(context, queryFace)

        assertArrayEquals(queryEmbedding, intent.getFloatArrayExtra(SimilarFacesActivity.EXTRA_QUERY_EMBEDDING)!!, 0f)
        assertArrayEquals(
            floatArrayOf(queryBox.left, queryBox.top, queryBox.right, queryBox.bottom),
            intent.getFloatArrayExtra(SimilarFacesActivity.EXTRA_QUERY_BOX)!!,
            0f,
        )
    }

    @Test
    fun `onCreate shows a grid of the matches returned by findMatches`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = SimilarFacesActivity.createIntent(context, queryFace)
        val match = FaceMatch(
            Uri.parse("content://media/external/images/media/1"),
            ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), queryEmbedding),
            similarity = 0.9f,
        )

        val controller = Robolectric.buildActivity(SimilarFacesActivity::class.java, intent)
        controller.get().findMatches = { listOf(match) }
        controller.create()

        val grid = controller.get().findViewById<GridView>(R.id.similar_faces_grid)
        assertEquals(View.VISIBLE, grid.visibility)
        assertEquals(1, grid.adapter.count)
    }

    @Test
    fun `onCreate shows the empty-state text when there are no matches`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = SimilarFacesActivity.createIntent(context, queryFace)

        val controller = Robolectric.buildActivity(SimilarFacesActivity::class.java, intent)
        controller.get().findMatches = { emptyList() }
        controller.create()

        val statusText = controller.get().findViewById<TextView>(R.id.similar_faces_status_text)
        val grid = controller.get().findViewById<GridView>(R.id.similar_faces_grid)
        assertEquals(View.VISIBLE, statusText.visibility)
        assertEquals(View.GONE, grid.visibility)
    }

    @Test
    fun `tapping a match opens fullscreen for just that photo`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = SimilarFacesActivity.createIntent(context, queryFace)
        val matchedUri = Uri.parse("content://media/external/images/media/42")
        val match = FaceMatch(matchedUri, ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), queryEmbedding), similarity = 0.9f)

        val controller = Robolectric.buildActivity(SimilarFacesActivity::class.java, intent)
        controller.get().findMatches = { listOf(match) }
        controller.create()

        val grid = controller.get().findViewById<GridView>(R.id.similar_faces_grid)
        grid.performItemClick(grid.getChildAt(0), 0, 0)

        val started = shadowOf(controller.get()).nextStartedActivity
        val startedUris = started.getParcelableArrayListExtra(FullscreenPhotoActivity.EXTRA_PHOTO_URIS, Uri::class.java)
        assertEquals(listOf(matchedUri), startedUris)
    }

    @Test
    fun `the default findMatches excludes the tapped face from its own results`() {
        // Regression test for the self-match bug: SimilarFacesActivity only ever sees a
        // reconstructed ScannedFace (from Intent extras), never the same instance FaceScanCache
        // holds - reference-based exclusion silently let the tapped face match itself at ~1.0.
        val context = ApplicationProvider.getApplicationContext<Context>()
        val uri = Uri.parse("content://media/external/images/media/self-exclusion-regression")
        val other = ScannedFace(NormalizedFaceBox(0f, 0f, 1f, 1f), floatArrayOf(0.9f, 0.1f, 0.1f))
        FaceScanCache.clear()
        FaceScanCache.put(uri, listOf(ScannedFace(queryBox, queryEmbedding), other))
        val intent = SimilarFacesActivity.createIntent(context, queryFace)

        val controller = Robolectric.buildActivity(SimilarFacesActivity::class.java, intent)
        controller.create()

        val grid = controller.get().findViewById<GridView>(R.id.similar_faces_grid)
        assertEquals(1, grid.adapter.count)
        assertFalse((0 until grid.adapter.count).any { (grid.adapter.getItem(it) as FaceMatch).face == queryFace })
    }
}
