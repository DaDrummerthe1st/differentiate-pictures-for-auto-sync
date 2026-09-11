package com.dpfas.photobrowser.triage

import android.content.Context
import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import com.dpfas.photobrowser.R
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class TriageSwipeActivityTest {

    private val uris = listOf(
        Uri.parse("content://media/external/images/media/1"),
        Uri.parse("content://media/external/images/media/2"),
        Uri.parse("content://media/external/images/media/3"),
    )

    @Test
    fun `createIntent carries the photo uris`() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val intent = TriageSwipeActivity.createIntent(context, uris)

        assertEquals(uris, intent.getParcelableArrayListExtra(TriageSwipeActivity.EXTRA_PHOTO_URIS, Uri::class.java))
    }

    @Test
    fun `onCreate wires the grid to the full photo list`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageSwipeActivity.createIntent(context, uris)

        val controller = Robolectric.buildActivity(TriageSwipeActivity::class.java, intent)
        controller.create()

        val grid = controller.get().findViewById<android.widget.GridView>(R.id.triage_swipe_grid)
        assertEquals(3, grid.adapter.count)
    }

    @Test
    fun `committing a REMOVE shrinks the grid and invokes the remove stub`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageSwipeActivity.createIntent(context, uris)
        val activityController = Robolectric.buildActivity(TriageSwipeActivity::class.java, intent)
        activityController.create()
        val activity = activityController.get()
        var removedUri: Uri? = null
        activity.onRemove = { removedUri = it }

        activity.controller.commit(uris[1], SwipeGesture.Outcome.REMOVE)

        val grid = activity.findViewById<android.widget.GridView>(R.id.triage_swipe_grid)
        assertEquals(2, grid.adapter.count)
        assertEquals(uris[1], removedUri)
    }

    @Test
    fun `undo after a commit restores the grid to its original size`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageSwipeActivity.createIntent(context, uris)
        val activityController = Robolectric.buildActivity(TriageSwipeActivity::class.java, intent)
        activityController.create()
        val activity = activityController.get()
        activity.controller.commit(uris[0], SwipeGesture.Outcome.ORGANIZE)

        activity.controller.undoLast()

        val grid = activity.findViewById<android.widget.GridView>(R.id.triage_swipe_grid)
        assertEquals(3, grid.adapter.count)
    }

    @Test
    fun `committing ORGANIZE calls the organize stub, not the remove stub`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageSwipeActivity.createIntent(context, uris)
        val activityController = Robolectric.buildActivity(TriageSwipeActivity::class.java, intent)
        activityController.create()
        val activity = activityController.get()
        var organizedUri: Uri? = null
        var removeCalled = false
        activity.onOrganize = { organizedUri = it }
        activity.onRemove = { removeCalled = true }

        activity.controller.commit(uris[0], SwipeGesture.Outcome.ORGANIZE)

        assertEquals(uris[0], organizedUri)
        assertTrue(!removeCalled)
    }
}
