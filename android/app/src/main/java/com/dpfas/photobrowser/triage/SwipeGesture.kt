package com.dpfas.photobrowser.triage

/**
 * Option B (per-tile swipe) demo's drag math - pure, no View/MotionEvent dependency. Direction
 * mapping (right=organize/keep, left=remove) is documentation/tags/UX_FLOWS.md's confirmed
 * 2026-09-07 Tinder-convention mapping, reused grid-only per the 2026-09-09 design session.
 * Commit threshold and rotation feel are NOT specified anywhere (confirmed with that session) -
 * these are placeholder values for the comparison demo, not a settled design.
 */
object SwipeGesture {

    const val COMMIT_THRESHOLD_PX = 120f
    private const val MAX_ROTATION_DEGREES = 9f
    private const val ROTATION_DIVISOR = 15f

    enum class Outcome { REMOVE, ORGANIZE, CANCEL }

    data class Transform(val translateX: Float, val rotationDegrees: Float)

    /** Live visual feedback while dragging, for any horizontal offset [dx]. */
    fun transformFor(dx: Float): Transform {
        val rotation = (dx / ROTATION_DIVISOR).coerceIn(-MAX_ROTATION_DEGREES, MAX_ROTATION_DEGREES)
        return Transform(translateX = dx, rotationDegrees = rotation)
    }

    /** What releasing the drag at total horizontal offset [dx] should do. */
    fun outcomeFor(dx: Float): Outcome = when {
        dx <= -COMMIT_THRESHOLD_PX -> Outcome.REMOVE
        dx >= COMMIT_THRESHOLD_PX -> Outcome.ORGANIZE
        else -> Outcome.CANCEL
    }
}
