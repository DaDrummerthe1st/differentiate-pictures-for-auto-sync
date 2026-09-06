package com.dpfas.photobrowser

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager2.widget.ViewPager2
import coil3.load

/**
 * Shows a single photo full-screen, opened by tapping a thumbnail in the grid. Swiping moves
 * between all photos in the grid (via [ViewPager2]); each page supports pinch-to-zoom/pan
 * (via [io.getstream.photoview.PhotoView]).
 */
class FullscreenPhotoActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_PHOTO_URIS = "photo_uris"
        const val EXTRA_START_POSITION = "start_position"

        fun createIntent(context: Context, uris: List<Uri>, startPosition: Int): Intent =
            Intent(context, FullscreenPhotoActivity::class.java)
                .putParcelableArrayListExtra(EXTRA_PHOTO_URIS, ArrayList(uris))
                .putExtra(EXTRA_START_POSITION, startPosition)
    }

    var loadImage: (ImageView, Uri) -> Unit = { imageView, uri -> imageView.load(uri) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_fullscreen_photo)

        val uris = intent.getParcelableArrayListExtra(EXTRA_PHOTO_URIS, Uri::class.java) ?: return
        val startPosition = intent.getIntExtra(EXTRA_START_POSITION, 0)

        findViewById<ViewPager2>(R.id.fullscreen_pager).apply {
            adapter = FullscreenPhotoPagerAdapter(uris) { imageView, uri -> loadImage(imageView, uri) }
            setCurrentItem(startPosition, false)
        }
    }
}
