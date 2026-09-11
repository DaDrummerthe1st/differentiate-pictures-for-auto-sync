package com.dpfas.photobrowser.triage

import org.junit.Assert.assertEquals
import org.junit.Test

class SwipeGestureTest {

    @Test
    fun `outcomeFor is CANCEL for any offset within the commit threshold`() {
        assertEquals(SwipeGesture.Outcome.CANCEL, SwipeGesture.outcomeFor(0f))
        assertEquals(SwipeGesture.Outcome.CANCEL, SwipeGesture.outcomeFor(50f))
        assertEquals(SwipeGesture.Outcome.CANCEL, SwipeGesture.outcomeFor(-50f))
    }

    @Test
    fun `outcomeFor is REMOVE past the left threshold and ORGANIZE past the right threshold`() {
        assertEquals(SwipeGesture.Outcome.REMOVE, SwipeGesture.outcomeFor(-SwipeGesture.COMMIT_THRESHOLD_PX))
        assertEquals(SwipeGesture.Outcome.REMOVE, SwipeGesture.outcomeFor(-500f))
        assertEquals(SwipeGesture.Outcome.ORGANIZE, SwipeGesture.outcomeFor(SwipeGesture.COMMIT_THRESHOLD_PX))
        assertEquals(SwipeGesture.Outcome.ORGANIZE, SwipeGesture.outcomeFor(500f))
    }

    @Test
    fun `transformFor tracks the drag distance directly`() {
        val transform = SwipeGesture.transformFor(40f)

        assertEquals(40f, transform.translateX, 1e-3f)
    }

    @Test
    fun `transformFor clamps rotation instead of spinning the tile past a small tilt`() {
        val transform = SwipeGesture.transformFor(10_000f)

        assertEquals(9f, transform.rotationDegrees, 1e-3f)
    }
}
