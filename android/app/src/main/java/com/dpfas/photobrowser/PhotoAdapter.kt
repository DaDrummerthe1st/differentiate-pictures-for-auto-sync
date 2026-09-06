package com.dpfas.photobrowser

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.util.LruCache
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.ImageView
import java.util.concurrent.Executors

/** Grid of photo thumbnails, decoded off the main thread and cached in memory. */
class PhotoAdapter(
    private val context: Context,
    private val photoUris: List<Uri>,
) : BaseAdapter() {

    private val thumbnailSizePx = 150
    private val executor = Executors.newFixedThreadPool(4)
    private val mainHandler = Handler(Looper.getMainLooper())
    private val cache = object : LruCache<Uri, Bitmap>(32 * 1024 * 1024) {
        override fun sizeOf(key: Uri, value: Bitmap) = value.byteCount
    }

    override fun getCount() = photoUris.size

    override fun getItem(position: Int): Uri = photoUris[position]

    override fun getItemId(position: Int) = position.toLong()

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val imageView = (convertView ?: LayoutInflater.from(context)
            .inflate(R.layout.grid_item_photo, parent, false)) as ImageView

        val uri = photoUris[position]
        imageView.tag = uri
        imageView.setImageDrawable(null)

        cache.get(uri)?.let {
            imageView.setImageBitmap(it)
            return imageView
        }

        executor.execute {
            val bitmap = decodeSampledThumbnail(uri)
            if (bitmap != null) {
                cache.put(uri, bitmap)
                mainHandler.post {
                    // Only apply if this view hasn't been recycled for a different item.
                    if (imageView.tag == uri) {
                        imageView.setImageBitmap(bitmap)
                    }
                }
            }
        }

        return imageView
    }

    private fun decodeSampledThumbnail(uri: Uri): Bitmap? {
        val resolver = context.contentResolver

        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) }
            ?: return null

        var sampleSize = 1
        while (bounds.outWidth / (sampleSize * 2) >= thumbnailSizePx &&
            bounds.outHeight / (sampleSize * 2) >= thumbnailSizePx
        ) {
            sampleSize *= 2
        }

        val decodeOptions = BitmapFactory.Options().apply { inSampleSize = sampleSize }
        return resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, decodeOptions) }
    }
}
