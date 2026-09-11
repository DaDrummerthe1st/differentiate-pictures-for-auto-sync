package com.dpfas.photobrowser.triage

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class TriageSelectionTest {

    private val uri1 = Uri.parse("content://media/external/images/media/1")
    private val uri2 = Uri.parse("content://media/external/images/media/2")

    @Test
    fun `starts inactive with nothing selected`() {
        val selection = TriageSelection()

        assertFalse(selection.isActive)
        assertTrue(selection.selected.isEmpty())
    }

    @Test
    fun `long press activates selection mode and selects that tile`() {
        val selection = TriageSelection()

        selection.onLongPress(uri1)

        assertTrue(selection.isActive)
        assertEquals(setOf(uri1), selection.selected)
    }

    @Test
    fun `tap while inactive is not consumed, so normal browsing (fullscreen) still applies`() {
        val selection = TriageSelection()

        val consumed = selection.onTap(uri1)

        assertFalse(consumed)
        assertTrue(selection.selected.isEmpty())
    }

    @Test
    fun `tap while active toggles selection instead of opening fullscreen`() {
        val selection = TriageSelection()
        selection.onLongPress(uri1)

        val consumedOnAdd = selection.onTap(uri2)
        assertTrue(consumedOnAdd)
        assertEquals(setOf(uri1, uri2), selection.selected)

        val consumedOnRemove = selection.onTap(uri1)
        assertTrue(consumedOnRemove)
        assertEquals(setOf(uri2), selection.selected)
    }

    @Test
    fun `cancel exits selection mode entirely and clears the selection`() {
        val selection = TriageSelection()
        selection.onLongPress(uri1)
        selection.onTap(uri2)

        selection.cancel()

        assertFalse(selection.isActive)
        assertTrue(selection.selected.isEmpty())
    }

    @Test
    fun `clearAfterAction exits selection mode after Remove or Organize acts on it`() {
        val selection = TriageSelection()
        selection.onLongPress(uri1)

        selection.clearAfterAction()

        assertFalse(selection.isActive)
        assertTrue(selection.selected.isEmpty())
    }
}
