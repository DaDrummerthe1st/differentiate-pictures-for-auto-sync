package com.dpfas.photobrowser

import android.content.ContentUris
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.view.View
import android.widget.GridView
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

/**
 * Slice 0: the smallest thing that proves the toolchain works end to end.
 * Lists the device's photos in a grid. No editing, sync, or on-device
 * analysis - see documentation/mobile/TODO.md for what comes next.
 */
class MainActivity : AppCompatActivity() {

    private val readImagesPermission =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            android.Manifest.permission.READ_MEDIA_IMAGES
        } else {
            android.Manifest.permission.READ_EXTERNAL_STORAGE
        }

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) loadPhotos() else showDenied()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (ContextCompat.checkSelfPermission(this, readImagesPermission)
            == PackageManager.PERMISSION_GRANTED
        ) {
            loadPhotos()
        } else {
            requestPermissionLauncher.launch(readImagesPermission)
        }
    }

    private fun showDenied() {
        findViewById<TextView>(R.id.status_text).apply {
            setText(R.string.permission_denied)
            visibility = View.VISIBLE
        }
        findViewById<GridView>(R.id.photo_grid).visibility = View.GONE
    }

    private fun loadPhotos() {
        Thread {
            val uris = queryPhotoUris()
            runOnUiThread { showPhotos(uris) }
        }.start()
    }

    private fun queryPhotoUris(): List<Uri> {
        val uris = mutableListOf<Uri>()
        val collection = MediaStore.Images.Media.EXTERNAL_CONTENT_URI
        val projection = arrayOf(MediaStore.Images.Media._ID)
        val sortOrder = "${MediaStore.Images.Media.DATE_ADDED} DESC"

        contentResolver.query(collection, projection, null, null, sortOrder)?.use { cursor ->
            val idColumn = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
            while (cursor.moveToNext()) {
                val id = cursor.getLong(idColumn)
                uris.add(ContentUris.withAppendedId(collection, id))
            }
        }
        return uris
    }

    private fun showPhotos(uris: List<Uri>) {
        val statusText = findViewById<TextView>(R.id.status_text)
        val grid = findViewById<GridView>(R.id.photo_grid)

        if (uris.isEmpty()) {
            statusText.setText(R.string.no_photos)
            statusText.visibility = View.VISIBLE
            grid.visibility = View.GONE
            return
        }

        statusText.visibility = View.GONE
        grid.visibility = View.VISIBLE
        grid.adapter = PhotoAdapter(this, uris)
        grid.setOnItemClickListener { _, _, position, _ ->
            startActivity(FullscreenPhotoActivity.createIntent(this, uris, position))
        }
    }
}
