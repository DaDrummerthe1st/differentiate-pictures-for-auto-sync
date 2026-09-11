package com.dpfas.photobrowser.triage

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.GridView
import androidx.appcompat.app.AppCompatActivity
import com.dpfas.photobrowser.R
import com.google.android.material.snackbar.Snackbar

/**
 * Option B live demo (per-tile swipe, Tinder-style), per the 2026-09-09 design session spec:
 * right=organize/keep, left=remove (documentation/tags/UX_FLOWS.md's confirmed direction mapping,
 * reused grid-only), commit past [SwipeGesture.COMMIT_THRESHOLD_PX], an undo snackbar right after.
 * Remove/Organize are Toast/log stubs, not real persistence (confirmed with Joakim).
 */
class TriageSwipeActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "TriageSwipe"
        const val EXTRA_PHOTO_URIS = "photo_uris"

        fun createIntent(context: Context, uris: List<Uri>): Intent =
            Intent(context, TriageSwipeActivity::class.java)
                .putParcelableArrayListExtra(EXTRA_PHOTO_URIS, ArrayList(uris))
    }

    private lateinit var photoUris: MutableList<Uri>
    private lateinit var adapter: TriageSwipeAdapter

    // Not private - Robolectric tests drive it directly instead of simulating real drag touch
    // events, same as this project's stance on not exercising real gesture dispatch in tests.
    lateinit var controller: TriageSwipeController
    private lateinit var gridView: GridView

    var onRemove: (Uri) -> Unit = { uri -> Log.d(TAG, "Remove stub: $uri") }
    var onOrganize: (Uri) -> Unit = { uri -> Log.d(TAG, "Organize stub: $uri") }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_triage_swipe)

        photoUris = (intent.getParcelableArrayListExtra(EXTRA_PHOTO_URIS, Uri::class.java) ?: arrayListOf())
            .toMutableList()
        gridView = findViewById(R.id.triage_swipe_grid)

        controller = TriageSwipeController(
            photoUris,
            onRemove = { uri -> onRemove(uri); showUndoSnackbar("Removed") },
            onOrganize = { uri -> onOrganize(uri); showUndoSnackbar("Organized") },
            onListChanged = { adapter.notifyDataSetChanged() },
        )
        adapter = TriageSwipeAdapter(this, photoUris, onCommitted = { uri, outcome -> controller.commit(uri, outcome) })
        gridView.adapter = adapter
    }

    private fun showUndoSnackbar(verb: String) {
        Snackbar.make(gridView as View, verb, Snackbar.LENGTH_LONG)
            .setAction("UNDO") { controller.undoLast() }
            .show()
    }
}
