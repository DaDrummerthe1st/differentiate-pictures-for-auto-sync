package com.dpfas.photobrowser.triage

import android.net.Uri

/**
 * Option A (multi-select + bottom action bar) demo's selection state - pure, no Android View/
 * Activity dependency, so the actual selection logic is unit-testable without touch simulation.
 * Per the design-session spec (2026-09-09, grid-only, Remove/Organize backed by a Toast/log stub
 * for this comparison pass, not real persistence): long-press enters selection mode and selects
 * that tile; while active, a tap toggles instead of opening fullscreen; cancel exits entirely.
 */
class TriageSelection {

    var isActive: Boolean = false
        private set

    private val _selected = mutableSetOf<Uri>()

    // A snapshot copy, not a live view - callers (e.g. Remove/Organize) read this and then call
    // clearAfterAction() right after; without the copy they'd see their own just-captured set
    // go empty out from under them, since it'd be the same mutable instance.
    val selected: Set<Uri> get() = _selected.toSet()

    fun onLongPress(uri: Uri) {
        isActive = true
        _selected.add(uri)
    }

    /** Returns true if the tap was consumed as a selection toggle (caller should not also open fullscreen). */
    fun onTap(uri: Uri): Boolean {
        if (!isActive) return false
        if (!_selected.add(uri)) _selected.remove(uri)
        return true
    }

    fun cancel() {
        isActive = false
        _selected.clear()
    }

    /** After Remove/Organize acts on the current selection. */
    fun clearAfterAction() {
        isActive = false
        _selected.clear()
    }
}
