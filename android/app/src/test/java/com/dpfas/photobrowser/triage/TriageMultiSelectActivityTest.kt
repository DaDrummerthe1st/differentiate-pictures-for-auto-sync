package com.dpfas.photobrowser.triage

import android.content.Context
import android.net.Uri
import android.view.View
import android.widget.Button
import android.widget.GridView
import android.widget.TextView
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
class TriageMultiSelectActivityTest {

    private val uris = listOf(
        Uri.parse("content://media/external/images/media/1"),
        Uri.parse("content://media/external/images/media/2"),
    )

    @Test
    fun `long-pressing a tile enters selection mode and shows the top and bottom bars`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageMultiSelectActivity.createIntent(context, uris)
        val controller = Robolectric.buildActivity(TriageMultiSelectActivity::class.java, intent)
        controller.create()
        val activity = controller.get()
        val grid = activity.findViewById<GridView>(R.id.triage_multiselect_grid)

        grid.onItemLongClickListener?.onItemLongClick(grid, grid, 0, 0L)

        assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.selection_top_bar).visibility)
        assertEquals(View.VISIBLE, activity.findViewById<View>(R.id.selection_bottom_bar).visibility)
        assertEquals("1 selected", activity.findViewById<TextView>(R.id.selection_count_text).text.toString())
    }

    @Test
    fun `cancel button exits selection mode and hides the bars`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageMultiSelectActivity.createIntent(context, uris)
        val controller = Robolectric.buildActivity(TriageMultiSelectActivity::class.java, intent)
        controller.create()
        val activity = controller.get()
        val grid = activity.findViewById<GridView>(R.id.triage_multiselect_grid)
        grid.onItemLongClickListener?.onItemLongClick(grid, grid, 0, 0L)

        activity.findViewById<TextView>(R.id.cancel_selection_button).performClick()

        assertEquals(View.GONE, activity.findViewById<View>(R.id.selection_top_bar).visibility)
        assertEquals(View.GONE, activity.findViewById<View>(R.id.selection_bottom_bar).visibility)
    }

    @Test
    fun `remove button invokes the remove stub with the selected uris and exits selection mode`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageMultiSelectActivity.createIntent(context, uris)
        val controller = Robolectric.buildActivity(TriageMultiSelectActivity::class.java, intent)
        controller.create()
        val activity = controller.get()
        var removedUris: Set<Uri>? = null
        activity.onRemove = { removedUris = it }
        val grid = activity.findViewById<GridView>(R.id.triage_multiselect_grid)
        grid.onItemLongClickListener?.onItemLongClick(grid, grid, 0, 0L)
        grid.onItemClickListener?.onItemClick(grid, grid, 1, 1L)

        activity.findViewById<Button>(R.id.remove_button).performClick()

        assertEquals(setOf(uris[0], uris[1]), removedUris)
        assertEquals(View.GONE, activity.findViewById<View>(R.id.selection_top_bar).visibility)
    }

    @Test
    fun `organize button invokes the organize stub, not the remove stub`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageMultiSelectActivity.createIntent(context, uris)
        val controller = Robolectric.buildActivity(TriageMultiSelectActivity::class.java, intent)
        controller.create()
        val activity = controller.get()
        var organizedUris: Set<Uri>? = null
        var removeCalled = false
        activity.onOrganize = { organizedUris = it }
        activity.onRemove = { removeCalled = true }
        val grid = activity.findViewById<GridView>(R.id.triage_multiselect_grid)
        grid.onItemLongClickListener?.onItemLongClick(grid, grid, 0, 0L)

        activity.findViewById<Button>(R.id.organize_button).performClick()

        assertEquals(setOf(uris[0]), organizedUris)
        assertTrue(!removeCalled)
    }

    @Test
    fun `tapping a tile while not in selection mode opens fullscreen instead of selecting`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val intent = TriageMultiSelectActivity.createIntent(context, uris)
        val controller = Robolectric.buildActivity(TriageMultiSelectActivity::class.java, intent)
        controller.create()
        val activity = controller.get()
        val grid = activity.findViewById<GridView>(R.id.triage_multiselect_grid)

        grid.onItemClickListener?.onItemClick(grid, grid, 0, 0L)

        val started = org.robolectric.Shadows.shadowOf(activity).nextStartedActivity
        assertEquals(
            com.dpfas.photobrowser.FullscreenPhotoActivity::class.java.name,
            started.component?.className,
        )
    }
}
