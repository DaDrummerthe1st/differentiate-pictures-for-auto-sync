package com.dpfas.photobrowser

import android.net.Uri
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.RecyclerView
import io.getstream.photoview.PhotoView

/** Backs the swipeable fullscreen [androidx.viewpager2.widget.ViewPager2], one photo per page. */
class FullscreenPhotoPagerAdapter(
    private val photoUris: List<Uri>,
    private val loadImage: (ImageView, Uri) -> Unit,
) : RecyclerView.Adapter<FullscreenPhotoPagerAdapter.ViewHolder>() {

    class ViewHolder(val photoView: PhotoView) : RecyclerView.ViewHolder(photoView)

    override fun getItemCount() = photoUris.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val photoView = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_fullscreen_photo, parent, false) as PhotoView
        return ViewHolder(photoView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        loadImage(holder.photoView, photoUris[position])
    }
}
