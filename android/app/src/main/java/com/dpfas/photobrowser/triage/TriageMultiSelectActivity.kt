package com.dpfas.photobrowser.triage

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.GridView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.dpfas.photobrowser.FullscreenPhotoActivity
import com.dpfas.photobrowser.R

/**
 * Option A live demo (multi-select + bottom action bar), per the 2026-09-09 design session spec:
 * long-press enters selection mode, tap toggles while active, Remove/Organize act on the whole
 * selection. Remove/Organize are Toast/log stubs, not real persistence (confirmed with Joakim) -
 * grid-only, fullscreen browsing is unchanged when not in selection mode.
 */
class TriageMultiSelectActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "TriageMultiSelect"
        const val EXTRA_PHOTO_URIS = "photo_uris"

        fun createIntent(context: Context, uris: List<Uri>): Intent =
            Intent(context, TriageMultiSelectActivity::class.java)
                .putParcelableArrayListExtra(EXTRA_PHOTO_URIS, ArrayList(uris))
    }

    private val selection = TriageSelection()
    private lateinit var photoUris: List<Uri>
    private lateinit var adapter: TriageSelectionAdapter

    var onRemove: (Set<Uri>) -> Unit = { uris ->
        Log.d(TAG, "Remove stub: ${uris.size} photo(s) -> $uris")
        Toast.makeText(this, "Removed ${uris.size} photo(s)", Toast.LENGTH_SHORT).show()
    }

    var onOrganize: (Set<Uri>) -> Unit = { uris ->
        Log.d(TAG, "Organize stub: ${uris.size} photo(s) -> $uris")
        Toast.makeText(this, "Organize ${uris.size} photo(s)", Toast.LENGTH_SHORT).show()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_triage_multiselect)

        photoUris = intent.getParcelableArrayListExtra(EXTRA_PHOTO_URIS, Uri::class.java) ?: emptyList()
        adapter = TriageSelectionAdapter(this, photoUris, selection)

        val grid = findViewById<GridView>(R.id.triage_multiselect_grid)
        grid.adapter = adapter

        grid.setOnItemLongClickListener { _, _, position, _ ->
            selection.onLongPress(photoUris[position])
            refreshChrome()
            true
        }
        grid.setOnItemClickListener { _, _, position, _ ->
            val uri = photoUris[position]
            if (selection.onTap(uri)) {
                refreshChrome()
            } else {
                startActivity(FullscreenPhotoActivity.createIntent(this, photoUris, position))
            }
        }

        findViewById<TextView>(R.id.cancel_selection_button).setOnClickListener {
            selection.cancel()
            refreshChrome()
        }
        findViewById<Button>(R.id.remove_button).setOnClickListener {
            onRemove(selection.selected)
            selection.clearAfterAction()
            refreshChrome()
        }
        findViewById<Button>(R.id.organize_button).setOnClickListener {
            onOrganize(selection.selected)
            selection.clearAfterAction()
            refreshChrome()
        }
    }

    private fun refreshChrome() {
        findViewById<View>(R.id.selection_top_bar).visibility = if (selection.isActive) View.VISIBLE else View.GONE
        findViewById<View>(R.id.selection_bottom_bar).visibility = if (selection.isActive) View.VISIBLE else View.GONE
        findViewById<TextView>(R.id.selection_count_text).text =
            getString(R.string.triage_selected_count, selection.selected.size)
        adapter.notifyDataSetChanged()
    }
}
