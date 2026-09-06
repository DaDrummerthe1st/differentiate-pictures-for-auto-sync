package com.dpfas.photobrowser

import android.content.Context
import android.net.Uri
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import coil3.load
import coil3.size.Precision
import coil3.size.Size

/** Grid of photo thumbnails, loaded and cached by Coil. */
class PhotoAdapter(
    private val context: Context,
    private val photoUris: List<Uri>,
    private val loadImage: (ImageView, Uri) -> Unit = { imageView, uri ->
        // A fixed request size keeps the memory-cache key stable across GridView's view
        // recycling - relying on the (recycled) ImageView's measured size instead would vary
        // slightly between binds and defeat the cache, forcing a re-decode every time.
        // INEXACT precision lets a larger cached bitmap (e.g. from viewing this same photo
        // fullscreen) satisfy this smaller thumbnail request instead of requiring an exact
        // size match - confirmed via Coil's DebugLogger that EXACT (the default) was rejecting
        // those hits and falling back to a disk decode.
        imageView.load(uri) {
            size(THUMBNAIL_SIZE_PX, THUMBNAIL_SIZE_PX)
            precision(Precision.INEXACT)
        }
    },
) : BaseAdapter() {

    companion object {
        private const val THUMBNAIL_SIZE_PX = 300
    }

    override fun getCount() = photoUris.size

    override fun getItem(position: Int): Uri = photoUris[position]

    override fun getItemId(position: Int) = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val imageView = (convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.grid_item_photo, parent, false)) as ImageView

        loadImage(imageView, photoUris[position])

        return imageView
    }
}
