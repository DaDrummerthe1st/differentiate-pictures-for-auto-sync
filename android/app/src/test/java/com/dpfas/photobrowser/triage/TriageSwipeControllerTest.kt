package com.dpfas.photobrowser.triage

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class TriageSwipeControllerTest {

    private val uri1 = Uri.parse("content://media/external/images/media/1")
    private val uri2 = Uri.parse("content://media/external/images/media/2")
    private val uri3 = Uri.parse("content://media/external/images/media/3")

    @Test
    fun `commit with REMOVE removes the photo from the list and calls the remove stub`() {
        val photos = mutableListOf(uri1, uri2, uri3)
        val removed = mutableListOf<Uri>()
        var changed = false
        val controller = TriageSwipeController(photos, onRemove = { removed.add(it) }, onOrganize = {}, onListChanged = { changed = true })

        controller.commit(uri2, SwipeGesture.Outcome.REMOVE)

        assertEquals(listOf(uri1, uri3), photos)
        assertEquals(listOf(uri2), removed)
        assertTrue(changed)
    }

    @Test
    fun `commit with ORGANIZE removes the photo and calls the organize stub, not the remove stub`() {
        val photos = mutableListOf(uri1, uri2)
        val removed = mutableListOf<Uri>()
        val organized = mutableListOf<Uri>()
        val controller = TriageSwipeController(photos, onRemove = { removed.add(it) }, onOrganize = { organized.add(it) }, onListChanged = {})

        controller.commit(uri1, SwipeGesture.Outcome.ORGANIZE)

        assertEquals(listOf(uri2), photos)
        assertEquals(listOf(uri1), organized)
        assertTrue(removed.isEmpty())
    }

    @Test
    fun `commit with CANCEL leaves the list untouched and calls neither stub`() {
        val photos = mutableListOf(uri1, uri2)
        var removeCalls = 0
        var organizeCalls = 0
        val controller = TriageSwipeController(photos, onRemove = { removeCalls++ }, onOrganize = { organizeCalls++ }, onListChanged = {})

        controller.commit(uri1, SwipeGesture.Outcome.CANCEL)

        assertEquals(listOf(uri1, uri2), photos)
        assertEquals(0, removeCalls)
        assertEquals(0, organizeCalls)
    }

    @Test
    fun `undoLast reinserts the most recently committed photo at its original index`() {
        val photos = mutableListOf(uri1, uri2, uri3)
        val controller = TriageSwipeController(photos, onRemove = {}, onOrganize = {}, onListChanged = {})
        controller.commit(uri2, SwipeGesture.Outcome.REMOVE)

        controller.undoLast()

        assertEquals(listOf(uri1, uri2, uri3), photos)
    }

    @Test
    fun `undoLast is a no-op when there is nothing to undo`() {
        val photos = mutableListOf(uri1)
        val controller = TriageSwipeController(photos, onRemove = {}, onOrganize = {}, onListChanged = {})

        controller.undoLast()

        assertEquals(listOf(uri1), photos)
    }

    @Test
    fun `undoLast only reverses the single most recent commit, not earlier ones`() {
        val photos = mutableListOf(uri1, uri2, uri3)
        val controller = TriageSwipeController(photos, onRemove = {}, onOrganize = {}, onListChanged = {})
        controller.commit(uri1, SwipeGesture.Outcome.REMOVE)
        controller.commit(uri2, SwipeGesture.Outcome.REMOVE)

        controller.undoLast()

        assertEquals(listOf(uri2, uri3), photos)
    }
}
