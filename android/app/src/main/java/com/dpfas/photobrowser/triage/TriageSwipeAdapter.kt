package com.dpfas.photobrowser.triage

import android.content.Context
import android.net.Uri
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import coil3.load
import coil3.size.Precision
import com.dpfas.photobrowser.R

/** Option B demo's grid: each tile carries its own [SwipeTileTouchListener]. */
class TriageSwipeAdapter(
    private val context: Context,
    private val photoUris: List<Uri>,
    private val onCommitted: (Uri, SwipeGesture.Outcome) -> Unit,
    private val loadImage: (ImageView, Uri) -> Unit = { imageView, uri ->
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

        // A recycled view may still carry a leftover drag transform from whatever it was
        // showing before - reset it before rebinding to a (possibly different) photo.
        imageView.translationX = 0f
        imageView.rotation = 0f

        val uri = photoUris[position]
        loadImage(imageView, uri)
        imageView.setOnTouchListener(SwipeTileTouchListener(uri, onCommitted))

        return imageView
    }
}
