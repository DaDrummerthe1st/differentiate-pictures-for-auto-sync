package com.dpfas.photobrowser

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import coil3.load

/** Shows a single photo full-screen, opened by tapping a thumbnail in the grid. */
class FullscreenPhotoActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_PHOTO_URI = "photo_uri"

        fun createIntent(context: Context, uri: Uri): Intent =
            Intent(context, FullscreenPhotoActivity::class.java).putExtra(EXTRA_PHOTO_URI, uri)
    }

    var loadImage: (ImageView, Uri) -> Unit = { imageView, uri -> imageView.load(uri) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_fullscreen_photo)

        val uri = intent.getParcelableExtra(EXTRA_PHOTO_URI, Uri::class.java) ?: return
        loadImage(findViewById(R.id.fullscreen_photo), uri)
    }
}
