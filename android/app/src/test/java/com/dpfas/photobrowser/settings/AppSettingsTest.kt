package com.dpfas.photobrowser.settings

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class AppSettingsTest {

    @Test
    fun `showFaceBoxes defaults to off`() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        assertFalse(AppSettings(context).showFaceBoxes)
    }

    @Test
    fun `showFaceBoxes persists across separate instances, simulating an app restart`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        AppSettings(context).showFaceBoxes = true

        assertTrue(AppSettings(context).showFaceBoxes)
    }

    @Test
    fun `showFaceBoxes can be turned back off and that also persists`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        AppSettings(context).showFaceBoxes = true
        AppSettings(context).showFaceBoxes = false

        assertFalse(AppSettings(context).showFaceBoxes)
    }
}
