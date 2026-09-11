package com.dpfas.photobrowser

import android.content.ContentUris
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.GridView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.dpfas.photobrowser.facerecognition.FaceRecognitionPipeline
import com.dpfas.photobrowser.facerecognition.FaceScanCache
import com.dpfas.photobrowser.facerecognition.FaceScanRunner
import com.dpfas.photobrowser.facerecognition.MobileFaceNetEmbedder
import com.dpfas.photobrowser.facerecognition.PhotoBitmapLoader
import com.dpfas.photobrowser.facerecognition.YuNetFaceDetector
import com.dpfas.photobrowser.facerecognition.toScannedFace
import com.dpfas.photobrowser.triage.TriageMultiSelectActivity
import com.dpfas.photobrowser.triage.TriageSwipeActivity

/**
 * Slice 0: the smallest thing that proves the toolchain works end to end.
 * Lists the device's photos in a grid. No editing, sync, or on-device
 * analysis - see documentation/mobile/TODO.md for what comes next.
 */
class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "FaceScan"
    }

    private var currentUris: List<Uri> = emptyList()

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
        currentUris = uris
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

        startFaceScan(uris)
    }

    /**
     * Detection + embedding, plus a subtle box overlay in the fullscreen viewer (via
     * [FaceScanCache]) - no identity-confirmation UI yet, see documentation/mobile/TODO.md. Runs
     * once per launch over the currently visible photos; progress is visible via Logcat and a
     * summary Toast, meant purely to verify the pipeline works end to end on-device.
     */
    private fun startFaceScan(uris: List<Uri>) {
        Thread {
            val pipeline = FaceRecognitionPipeline(YuNetFaceDetector(this), MobileFaceNetEmbedder(this))
            val runner = FaceScanRunner(
                loadBitmap = { uri -> PhotoBitmapLoader.load(this, uri) },
                scan = { bitmap -> pipeline.scan(bitmap) },
                onPhotoScanned = { uri, index, total, imageWidth, imageHeight, results ->
                    if (imageWidth > 0 && imageHeight > 0) {
                        FaceScanCache.put(uri, results.map { it.toScannedFace(imageWidth, imageHeight) })
                    }
                    Log.d(TAG, "photo ${index + 1}/$total: ${results.size} face(s)")
                },
            )
            val totalFaces = runner.scanAll(uris)
            Log.d(TAG, "done: $totalFaces face(s) across ${uris.size} photo(s)")
            runOnUiThread {
                Toast.makeText(
                    this,
                    "Face scan: $totalFaces face(s) across ${uris.size} photo(s)",
                    Toast.LENGTH_LONG,
                ).show()
            }
        }.start()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean =
        when (item.itemId) {
            R.id.menu_triage_multiselect -> {
                startActivity(TriageMultiSelectActivity.createIntent(this, currentUris))
                true
            }
            R.id.menu_triage_swipe -> {
                startActivity(TriageSwipeActivity.createIntent(this, currentUris))
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
}
