package com.dpfas.photobrowser.triage

import android.net.Uri
import android.view.MotionEvent
import android.view.View

/**
 * Drives one grid tile's drag-to-triage gesture. Thin glue over [SwipeGesture]'s pure math (which
 * carries the actual test coverage) - not itself unit tested, same as this project's stance on
 * not exercising real touch dispatch/animation in Robolectric.
 */
class SwipeTileTouchListener(
    private val uri: Uri,
    private val onCommitted: (Uri, SwipeGesture.Outcome) -> Unit,
) : View.OnTouchListener {

    private var startX = 0f
    private var dx = 0f

    override fun onTouch(v: View, event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.rawX
                dx = 0f
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                dx = event.rawX - startX
                val transform = SwipeGesture.transformFor(dx)
                v.translationX = transform.translateX
                v.rotation = transform.rotationDegrees
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                val outcome = SwipeGesture.outcomeFor(dx)
                if (outcome == SwipeGesture.Outcome.CANCEL) {
                    v.animate().translationX(0f).rotation(0f).setDuration(150).start()
                } else {
                    val offScreenX = if (outcome == SwipeGesture.Outcome.REMOVE) -2000f else 2000f
                    v.animate()
                        .translationX(offScreenX)
                        .setDuration(200)
                        .withEndAction {
                            v.translationX = 0f
                            v.rotation = 0f
                            onCommitted(uri, outcome)
                        }
                        .start()
                }
                dx = 0f
                return true
            }
        }
        return false
    }
}
