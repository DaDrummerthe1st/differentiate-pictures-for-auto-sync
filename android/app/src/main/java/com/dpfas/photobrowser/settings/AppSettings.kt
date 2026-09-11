package com.dpfas.photobrowser.settings

import android.content.Context

/**
 * Persists user-toggleable app settings across app restarts (backed by [android.content.SharedPreferences]).
 * Every persistent toggle the app grows should be added here as another property following the
 * same pattern, rather than reading/writing preferences ad hoc elsewhere.
 */
class AppSettings(context: Context) {

    private val prefs = context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var showFaceBoxes: Boolean
        get() = prefs.getBoolean(KEY_SHOW_FACE_BOXES, false)
        set(value) {
            prefs.edit().putBoolean(KEY_SHOW_FACE_BOXES, value).apply()
        }

    private companion object {
        const val PREFS_NAME = "app_settings"
        const val KEY_SHOW_FACE_BOXES = "show_face_boxes"
    }
}
