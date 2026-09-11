package com.dpfas.photobrowser.triage

import android.net.Uri

/**
 * Option B demo's list mutation + undo, separated from touch/animation glue so it's unit-testable
 * without simulating drag gestures. Remove/Organize are Toast/log stubs for this comparison pass
 * (confirmed with Joakim 2026-09-09) - [onRemove]/[onOrganize] are exactly that stub, not real
 * persistence.
 */
class TriageSwipeController(
    private val photoUris: MutableList<Uri>,
    private val onRemove: (Uri) -> Unit,
    private val onOrganize: (Uri) -> Unit,
    private val onListChanged: () -> Unit,
) {
    private var lastRemovedIndex = -1
    private var lastRemovedUri: Uri? = null

    fun commit(uri: Uri, outcome: SwipeGesture.Outcome) {
        if (outcome == SwipeGesture.Outcome.CANCEL) return
        val index = photoUris.indexOf(uri)
        if (index == -1) return

        photoUris.removeAt(index)
        lastRemovedIndex = index
        lastRemovedUri = uri
        onListChanged()

        when (outcome) {
            SwipeGesture.Outcome.REMOVE -> onRemove(uri)
            SwipeGesture.Outcome.ORGANIZE -> onOrganize(uri)
            SwipeGesture.Outcome.CANCEL -> Unit
        }
    }

    /** Reinserts the most recently committed photo at its original position. No-op if nothing to undo, or undo was already used once. */
    fun undoLast() {
        val uri = lastRemovedUri ?: return
        photoUris.add(lastRemovedIndex.coerceIn(0, photoUris.size), uri)
        lastRemovedUri = null
        onListChanged()
    }
}
